#!/usr/bin/env python3
"""나무위키에서 한국 개봉작의 쿠키 정보를 모아 로컬 색인을 만든다.

aftercredits·mediastinger 색인이 놓치는 자리를 메운다. 그 둘은 영어권 개봉작
중심이라 한국·일본 영화가 통째로 빈다 — 정작 이 앱을 쓰는 사람이 가장 많이
찾는 쪽이다.

**키는 TMDB id 다.** 다른 색인처럼 제목으로 키를 잡으면 안 된다:
normalize_title 이 `[^a-z0-9]` 를 지우기 때문에 '경주기행' 같은 제목은 빈
문자열이 되어 서로 다른 영화가 한 칸에 뭉개진다. id 는 그런 문제가 없다.

한 번에 다 훑지 않는다. 문서당 1초를 지켜야 하고 후보가 수천 편이라, 매 실행
budget 만큼만 새로 보고 다음 실행이 이어받는다. 판정이 안 난 영화도 기록해 둬야
(checked) 매번 같은 문서를 다시 두드리지 않는다.

출력: data/ko-index.json
  { "syncedAt": ISO, "entries": {"<tmdbId>": {"s","d","a","u"}}, "checked": [tmdbId...] }

사용법:
  python3 tools/sync_namu.py                 # 기본 budget 만큼 이어서
  python3 tools/sync_namu.py --budget 300
  python3 tools/sync_namu.py --years 2020 2026
"""

import datetime
import json
import os
import pathlib
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sources  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "data" / "ko-index.json"

DEFAULT_BUDGET = 150
DEFAULT_YEARS = (2016, 2026)
PAGES_PER_YEAR = 5          # 연도당 TMDB 인기순 상위 100편


def tmdb_get(path, **params):
    token = os.environ.get("TMDB_READ_TOKEN")
    if not token:
        sys.exit("TMDB_READ_TOKEN 이 필요합니다")
    url = "https://api.themoviedb.org/3" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def candidates(years):
    """한국에서 개봉한 작품을 연도별 인기순으로. 한국·일본 영화가 앞에 오도록
    원어를 우선하되, 그 밖의 언어도 뒤에 붙인다 (영어권 색인이 놓친 것들)."""
    seen = set()
    out = []
    for year in range(years[0], years[1] + 1):
        for lang in ("ko", "ja", None):
            for page in range(1, PAGES_PER_YEAR + 1):
                params = {
                    "region": "KR",
                    "language": "ko-KR",
                    "sort_by": "popularity.desc",
                    "primary_release_year": year,
                    "page": page,
                }
                if lang:
                    params["with_original_language"] = lang
                try:
                    data = tmdb_get("/discover/movie", **params)
                except Exception:
                    continue
                for m in data.get("results", []):
                    if m["id"] in seen:
                        continue
                    seen.add(m["id"])
                    out.append(m)
                if page >= data.get("total_pages", 1):
                    break
    return out


def directors_of(tmdb_id):
    try:
        crew = tmdb_get(f"/movie/{tmdb_id}/credits", language="ko-KR").get("crew", [])
    except Exception:
        return []
    return [c["name"] for c in crew if c.get("job") == "Director"]


def main():
    argv = sys.argv
    budget = int(argv[argv.index("--budget") + 1]) if "--budget" in argv else DEFAULT_BUDGET
    years = DEFAULT_YEARS
    if "--years" in argv:
        i = argv.index("--years")
        years = (int(argv[i + 1]), int(argv[i + 2]))

    # 나무위키가 막혀 있는지 먼저 본다. GitHub Actions 러너 IP 는 Cloudflare 에
    # 자주 걸리는데, 그걸 모르고 돌면 '문서를 못 읽음'과 '쿠키 언급이 없음'이
    # 구분되지 않아 멀쩡한 영화 수백 편이 checked 로 타버린다 — 그러면 다시는
    # 조회되지 않는다. 확실히 있는 문서 하나로 확인하고, 안 되면 그냥 나간다.
    if not sources._namu_fetch_text("쿠키 영상"):
        print("나무위키에 접근할 수 없습니다 (차단 가능성) — 이번 실행은 건너뜁니다")
        return

    index = {"syncedAt": None, "entries": {}, "checked": []}
    if INDEX_PATH.exists():
        index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    checked = set(index.get("checked", []))

    print(f"나무위키 동기화 — {years[0]}~{years[1]}년, 이번 실행 최대 {budget}편")
    pool = [m for m in candidates(years) if m["id"] not in checked]
    print(f"  후보 {len(pool)}편 (이미 확인 {len(checked)}편)")

    found = 0
    for n, m in enumerate(pool[:budget], 1):
        title = m.get("title") or ""
        year = int((m.get("release_date") or "0000")[:4] or 0) or None
        hit = None
        try:
            hit = sources.namu_lookup(title, year, directors_of(m["id"]))
        except Exception as e:
            print(f"  ! {title}: {e}")
        checked.add(m["id"])
        if hit and hit.get("status") in ("yes", "no"):
            cookies = hit.get("cookies") or []
            index["entries"][str(m["id"])] = {
                "s": hit["status"],
                "d": 1 if any(c.get("pos") == "크레딧 중간" for c in cookies) else 0,
                "a": 1 if any(c.get("pos") == "크레딧 종료 후" for c in cookies) else 0,
                "u": hit.get("sourceUrl") or "",
            }
            found += 1
            print(f"  [{n}/{min(budget, len(pool))}] {title} → {hit['status']}")
        if n % 25 == 0:
            print(f"  … {n}편 확인 · 판정 {found}편")
            save(index, checked)

    save(index, checked)
    yes = sum(1 for e in index["entries"].values() if e["s"] == "yes")
    print(f"완료 — 색인 {len(index['entries'])}편 (있음 {yes} · 없음 {len(index['entries']) - yes})"
          f" · 확인 누적 {len(checked)}편 → {INDEX_PATH}")


def save(index, checked):
    index["checked"] = sorted(checked)
    index["syncedAt"] = datetime.datetime.now().isoformat(timespec="seconds")
    INDEX_PATH.parent.mkdir(exist_ok=True)
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
