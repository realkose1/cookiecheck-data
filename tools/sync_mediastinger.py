#!/usr/bin/env python3
"""mediastinger.com 카탈로그를 로컬 색인으로 동기화한다.

aftercredits 색인(sync_aftercredits.py)과 같은 역할·같은 형식이다. 두 곳이
겹치는 영화도 많지만 서로 놓치는 것도 많아서, 합치면 '미확인'이 줄어든다.
특히 mediastinger 는 개봉 중인 작품을 더 빨리 올린다.

aftercredits 와 달리 REST API 가 막혀 있어(iThemes Security) HTML 을 읽는다.
개별 영화 페이지를 하나씩 여는 대신 **판정별 카테고리 목록**을 훑는다 —
카테고리가 곧 판정이라 목록 한 페이지(26편)에서 26편이 한 번에 정해진다.

robots.txt 가 Crawl-delay: 10 을 요구하므로 요청 사이를 그만큼 띄운다.
전체 훑기는 30분 남짓 걸리니 처음 한 번만 로컬에서 돌리고, 이후에는 각
카테고리 앞쪽 몇 페이지만 보는 증분으로 돈다 (새 글이 앞에 쌓이는 구조).

출력: data/ms-index.json  (형식은 ac-index.json 과 동일)
  { "syncedAt": ISO8601, "entries": { "<정규화제목>|<연도>": {"s","d","a","u"} } }

사용법:
  python3 tools/sync_mediastinger.py            # 증분 (카테고리별 앞 3페이지)
  python3 tools/sync_mediastinger.py --full     # 전체
  python3 tools/sync_mediastinger.py --pages 8  # 증분 깊이 지정
"""

import datetime
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from sources import normalize_title  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "data" / "ms-index.json"
BASE = "https://mediastinger.com/type-of-stinger"
UA = "cookiecheck/0.1 (+personal project)"

# robots.txt 의 Crawl-delay. 줄이지 말 것 — 남의 서버다.
DELAY = 10
INCREMENTAL_PAGES = 3

# 카테고리 → (판정, 크레딧 중간, 크레딧 종료 후)
#
# 'currently-no-after-credits-information' 은 담지 않는다. 색인해봐야 미확인이라
# 결과가 같고, 오히려 나중에 판정이 붙었을 때 낡은 값이 남는다.
#
# 'scene-during-credits' / 'extras-during-credits' 도 **일부러 뺐다.** 이 사이트는
# 크레딧 위에 얹힌 장식까지 그 분류에 넣는다 — 모탈 컴뱃 II 는 "배우 이름 주위로
# 영상 요소가 회전한다"가 근거다. 그걸 '쿠키 있음'으로 알리면 관객을 빈 극장에
# 10분 앉혀 두게 된다. 실제로 aftercredits 와 어긋난 327건 중 288건이 이 분류였다.
# 크레딧 중간 쿠키는 판정이 더 엄격한 aftercredits 색인에 맡긴다.
CATEGORIES = {
    "no-post-credits-scene": ("no", 0, 0),
    "post-credits-scene": ("yes", 0, 1),
    "post-credits-extra": ("yes", 0, 1),
}

ITEM_RE = re.compile(r'class="title" ><a href="([^"]+)">([^<]+)</a>')
PAGE_RE = re.compile(r"/page/(\d+)/")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def year_of(title):
    m = re.search(r"\((19|20)\d{2}\)", title)
    return m.group(0)[1:-1] if m else ""


def crawl(slug, verdict, limit, entries):
    """카테고리 목록을 페이지 단위로 훑는다. 새로 담은 편수를 돌려준다."""
    status, during, after = verdict
    added = 0
    page, last = 1, None
    while True:
        url = f"{BASE}/{slug}/" if page == 1 else f"{BASE}/{slug}/page/{page}/"
        try:
            html = fetch(url)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                break  # 마지막 페이지를 지났다
            raise

        items = ITEM_RE.findall(html)
        if not items:
            break
        for link, raw in items:
            key = f"{normalize_title(raw)}|{year_of(raw)}"
            # 같은 영화가 여러 카테고리에 걸리면 '있음' 을 이긴 것으로 둔다 —
            # 중간/종료 후가 각각 다른 카테고리라 둘 다 달릴 수 있기 때문.
            old = entries.get(key)
            if old and old["s"] == "yes":
                old["d"] = old["d"] or during
                old["a"] = old["a"] or after
                continue
            entries[key] = {"s": status, "d": during, "a": after, "u": link}
            added += 1

        if last is None:
            nums = [int(n) for n in PAGE_RE.findall(html)]
            last = max(nums) if nums else 1
        print(f"  {slug} {page}/{last if limit is None else min(last, limit)} · 누적 {added}편")

        page += 1
        if page > last or (limit is not None and page > limit):
            break
        time.sleep(DELAY)
    return added


def main():
    full = "--full" in sys.argv
    limit = None if full else INCREMENTAL_PAGES
    if "--pages" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--pages") + 1])

    index = {"syncedAt": None, "entries": {}}
    if INDEX_PATH.exists() and not full:
        index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))

    print(f"mediastinger 동기화 시작 — {'전체' if full else f'증분 (카테고리당 {limit}페이지)'}")
    total = 0
    for slug, verdict in CATEGORIES.items():
        total += crawl(slug, verdict, limit, index["entries"])
        time.sleep(DELAY)

    index["syncedAt"] = datetime.datetime.now().isoformat(timespec="seconds")
    INDEX_PATH.parent.mkdir(exist_ok=True)
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")

    yes = sum(1 for e in index["entries"].values() if e["s"] == "yes")
    no = len(index["entries"]) - yes
    print(f"완료 — 색인 {len(index['entries'])}편 (있음 {yes} · 없음 {no}) · 이번에 {total}편 → {INDEX_PATH}")


if __name__ == "__main__":
    main()
