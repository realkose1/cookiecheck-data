#!/usr/bin/env python3
"""aftercredits.com 전체 카탈로그를 로컬 색인으로 동기화한다.

검색 기능의 뼈대다: 사용자가 아무 영화나 검색하면(TMDB), 그 영화의 쿠키 유무를
이 색인에서 즉시 대조한다. 영화당 API 를 부르는 대신 카탈로그 전체(~7,900편)를
한 번 받아두고, 이후에는 마지막 동기화 이후 글만 증분으로 받는다.

판정은 카테고리로만 한다 (본문은 받지 않는다 — 100편씩 79페이지로 끝나는 이유):
  7  Stingers          → yes        6  Non-Stingers      → no
  14 During Credits    → 중간        15 After Credits     → 종료 후
  16 Both During&After → 중간+종료 후  8  Unknown           → unknown

출력: data/ac-index.json
  { "syncedAt": ISO8601, "entries": { "<정규화제목>|<연도>": {"s","d","a","u"} } }
  s: yes|no|unknown · d/a: 중간/종료후 쿠키 존재(0|1) · u: 출처 URL

사용법:
  python3 tools/sync_aftercredits.py          # 증분 (색인 없으면 전체)
  python3 tools/sync_aftercredits.py --full   # 전체 다시
"""

import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from sources import normalize_title  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "data" / "ac-index.json"
API = "https://aftercredits.com/wp-json/wp/v2/posts"
UA = "cookiecheck/0.1 (+personal project)"

CAT_MOVIES = 5
CAT_STINGERS, CAT_NON, CAT_UNKNOWN = 7, 6, 8
CAT_DURING, CAT_AFTER, CAT_BOTH = 14, 15, 16


def fetch_page(page, after=None):
    params = {
        "categories": CAT_MOVIES,
        "per_page": 100,
        "page": page,
        "_fields": "title,link,categories,date",
        "orderby": "date",
        "order": "desc",
    }
    if after:
        params["after"] = after
    req = urllib.request.Request(
        f"{API}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": UA, "accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        total_pages = int(r.headers.get("X-WP-TotalPages", "1"))
        return json.load(r), total_pages


def year_of(title):
    m = re.search(r"\((19|20)\d{2}\)", title)
    return m.group(0)[1:-1] if m else ""


def entry_of(post):
    cats = set(post.get("categories") or [])
    if CAT_STINGERS in cats:
        status = "yes"
    elif CAT_NON in cats:
        status = "no"
    else:
        return None  # Unknown / 분류 없음 — 색인해봐야 미확인이라 뺀다

    return {
        "s": status,
        "d": 1 if (CAT_DURING in cats or CAT_BOTH in cats) else 0,
        "a": 1 if (CAT_AFTER in cats or CAT_BOTH in cats) else 0,
        "u": post["link"],
    }


def main():
    index = {"syncedAt": None, "entries": {}}
    if INDEX_PATH.exists() and "--full" not in sys.argv:
        index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))

    after = index["syncedAt"] if "--full" not in sys.argv else None
    mode = f"증분 (after {after})" if after else "전체"
    print(f"aftercredits 동기화 시작 — {mode}")

    page, total_pages, added = 1, 1, 0
    newest_date = index["syncedAt"]
    while page <= total_pages:
        try:
            posts, total_pages = fetch_page(page, after)
        except urllib.error.HTTPError as e:
            if e.code == 400 and page > 1:
                break  # 페이지 범위 초과 (증분에서 발생 가능)
            raise
        for post in posts:
            raw = re.sub(r"<[^>]+>", "", post["title"]["rendered"])
            entry = entry_of(post)
            if entry is None:
                continue
            key = f"{normalize_title(raw)}|{year_of(raw)}"
            index["entries"][key] = entry
            added += 1
            if not newest_date or post["date"] > newest_date:
                newest_date = post["date"]
        print(f"  {page}/{total_pages} 페이지 · 누적 {added}편")
        page += 1
        time.sleep(0.4)  # 남의 서버

    index["syncedAt"] = newest_date
    INDEX_PATH.parent.mkdir(exist_ok=True)
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")

    yes = sum(1 for e in index["entries"].values() if e["s"] == "yes")
    no = len(index["entries"]) - yes
    print(f"완료 — 색인 {len(index['entries'])}편 (있음 {yes} · 없음 {no}) → {INDEX_PATH}")

    # iOS 번들 사본
    ios_data = ROOT / "ios" / "data"
    if ios_data.exists():
        (ios_data / "ac-index.json").write_text(
            json.dumps(index, ensure_ascii=False), encoding="utf-8"
        )
        print("  ios/data/ac-index.json 갱신")


if __name__ == "__main__":
    main()
