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

**순서: 현재 피드(상영작) 먼저, 남은 예산만 백카탈로그.** 백카탈로그를 앞에
두면 수천 편을 다 훑을 때까지 정작 지금 극장에 걸린 영화가 색인에 안 들어온다.
그리고 개봉 60일 이내의 미확인 상영작은 checked 에 있어도 다시 본다 — 개봉
직후엔 문서에 쿠키 문단이 없다가 며칠 뒤 생기기 때문 (RECHECK_DAYS 참고).

출력: data/ko-index.json
  { "syncedAt": ISO, "entries": {"<tmdbId>": {"s","d","a","u","t"?}}, "checked": [...] }
  t 는 쿠키 설명(한국어). 문서에 알맹이 있는 서술이 있을 때만 담는다.

사용법:
  python3 tools/sync_namu.py                 # 기본 budget 만큼 이어서
  python3 tools/sync_namu.py --budget 300
  python3 tools/sync_namu.py --years 2020 2026
"""

import datetime
import json
import os
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sources  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "data" / "ko-index.json"
FEED_PATH = ROOT / "ios" / "data" / "cookies.json"

DEFAULT_BUDGET = 150
DEFAULT_YEARS = (2016, 2026)
PAGES_PER_YEAR = 5          # 연도당 TMDB 인기순 상위 100편

# 상영작 재확인 기간. 개봉 직후에는 나무위키 문서에 쿠키 문단이 아직 없다가
# 며칠~몇 주 뒤에 생긴다 — 한 번 못 찾았다고 checked 에 넣고 영원히 안 보면
# 정작 지금 극장에 걸린 영화가 끝까지 '미확인'으로 남는다 (이번 사고가 그것이다).
# 그래서 피드에 있고 아직 판정이 없는 작품은 개봉 후 이 기간 동안 매번 다시 본다.
# 60일은 국내 상영 주기(대개 4~8주)를 넉넉히 덮는 길이다. 이미 판정이 난 작품은
# 다시 보지 않는다 — 쿠키 유무는 변하지 않는 사실이라 재확인할 이유가 없다.
RECHECK_DAYS = 60


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


def feed_candidates():
    """지금 앱이 보여주는 작품 목록 (ios/data/cookies.json).

    백카탈로그를 연도순으로 기어가는 것보다 **이쪽이 먼저다.** 색인이 필요한
    이유는 러너가 상영작 쿠키를 못 채우기 때문인데, discover 를 앞에 두면
    수천 편을 다 훑을 때까지 정작 지금 상영 중인 영화가 색인에 안 들어온다.
    """
    try:
        feed = json.loads(FEED_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
    out = []
    for m in feed.get("movies", []):
        if not m.get("tmdbId"):
            continue
        out.append({
            "id": m["tmdbId"],
            "title": m.get("title") or "",
            "release_date": m.get("releaseDate") or "",
            "_status": m.get("status"),
        })
    return out


def _recheck_ok(m, today):
    """checked 에 있어도 다시 봐야 하는 상영작인가 (RECHECK_DAYS 주석 참고)."""
    if m.get("_status") != "unknown":
        return False
    try:
        released = datetime.date.fromisoformat(m.get("release_date") or "")
    except ValueError:
        return False
    return 0 <= (today - released).days <= RECHECK_DAYS


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


# 존재만 알리는 문장은 담지 않는다 — 필 배지와 위치 표시가 이미 같은 말을 한다.
# 쿠키를 쪼갰는데 "쿠키 영상이 존재한다" 가 나오면 쪼갠 보람이 없다.
_EXISTENCE = re.compile(
    r"쿠키\s*영상(은|이|가|도)?\s*(총\s*\d+\s*개(가)?\s*)?"
    r"(있다|없다|존재한다|나온다|있음|없음|있습니다|나옵니다)"
)


def _clean_desc(text):
    """나무위키 본문에서 뽑은 문장의 찌꺼기를 턴다 (문단 기호, 목차 번호)."""
    t = re.sub(r"^#+\s*", "", (text or "").strip())
    t = re.sub(r"^(\d+(\.\d+)*\s+)+", "", t)
    return re.sub(r"\s+", " ", t).strip()


def _is_thin(text):
    rest = re.sub(r"[\s.,·…!?~\-—()\[\]'\"]+", "", _EXISTENCE.sub("", text))
    return len(rest) < 10


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
    entries = index.setdefault("entries", {})
    today = datetime.date.today()

    print(f"나무위키 동기화 — {years[0]}~{years[1]}년, 이번 실행 최대 {budget}편")

    # 1) 현재 피드(= 앱이 지금 보여주는 상영작)를 맨 앞에.
    #    판정이 이미 있으면 건너뛰고, checked 에 있더라도 개봉 60일 이내의
    #    미확인작이면 문서가 그새 자랐을 수 있으니 다시 본다.
    feed = feed_candidates()
    front = []
    for m in feed:
        if str(m["id"]) in entries:
            continue
        if m["id"] in checked and not _recheck_ok(m, today):
            continue
        front.append(m)

    # 2) 남은 예산만 백카탈로그에. 상영작만으로 예산이 차면 discover 는 아예
    #    부르지 않는다 — TMDB 요청 수백 번을 아낀다.
    front = front[:budget]
    rechecks = sum(1 for m in front if m["id"] in checked)
    remaining = budget - len(front)
    back = []
    if remaining > 0:
        front_ids = {m["id"] for m in front}
        back = [
            m for m in candidates(years)
            if m["id"] not in checked and m["id"] not in front_ids and str(m["id"]) not in entries
        ]
    pool = front + back[:remaining]
    print(f"  상영작 {len(front)}편 (재확인 {rechecks}편) + 백카탈로그 {len(pool) - len(front)}편"
          f" · 후보 풀 {len(back)}편 · 이미 확인 {len(checked)}편")

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
            entry = {
                "s": hit["status"],
                "d": 1 if any(c.get("pos") == "크레딧 중간" for c in cookies) else 0,
                "a": 1 if any(c.get("pos") == "크레딧 종료 후" for c in cookies) else 0,
                "u": hit.get("sourceUrl") or "",
            }
            # 쿠키 설명. 나무위키는 한국어라 번역이 필요 없다 — 그냥 담아두면
            # 검색 결과에서도 "쿠키가 있다"에서 그치지 않고 내용을 보여줄 수 있다.
            # 위치별로 나누지 않고 한 줄만 둔다 (문서 서술이 그 정도 입자다).
            desc = _clean_desc(next((c.get("desc") for c in cookies if c.get("desc")), ""))
            if desc and not _is_thin(desc):
                entry["t"] = desc[:400]
            index["entries"][str(m["id"])] = entry
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
