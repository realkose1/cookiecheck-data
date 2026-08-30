#!/usr/bin/env python3
"""data.js 갱신 — TMDB에서 한국 현재 상영작을 받아온다.

SweetSpot(ios/Sources/Services/TMDBService.swift)과 같은 방식이다:
  - /movie/now_playing?region=KR&language=ko-KR 로 목록을 받고
  - /movie/{id}/release_dates 의 KR 항목에서 실제 국내 개봉일을 뽑는다
    (type 우선순위 3 극장 > 2 극장 제한 > 1 프리미어, 같은 type 안에서는 최소값)

쿠키(쿠키 영상) 정보는 TMDB에 없어서 tools/sources.py 가 따로 채운다.
우선순위: data.overrides.json > aftercredits.com > TMDB 키워드 > 미확인.

사용법:
  export TMDB_READ_TOKEN="<TMDB v4 read access token>"
  python3 tools/fetch_movies.py

토큰은 SweetSpot 에 이미 있다:
  grep '^TMDB_READ_TOKEN' ~/Desktop/SweetSpot/ios/Config/Secrets.xcconfig
"""

import datetime
import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sources  # noqa: E402

API = "https://api.themoviedb.org/3"
ROOT = pathlib.Path(__file__).resolve().parent.parent
MAX_MOVIES = 18
PAGES = (1, 2)

TOKEN = os.environ.get("TMDB_READ_TOKEN", "").strip()
if not TOKEN:
    sys.exit("TMDB_READ_TOKEN 환경변수가 필요합니다. (docstring 참고)")


def get(path, **params):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {TOKEN}", "accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def kr_release_date(detail):
    """KR 극장 개봉일. 없으면 TMDB 기본 release_date 로 폴백."""
    for country in detail.get("release_dates", {}).get("results", []):
        if country["iso_3166_1"] != "KR":
            continue
        entries = country["release_dates"]
        for preferred in (3, 2, 1):
            dates = [e["release_date"][:10] for e in entries if e["type"] == preferred]
            if dates:
                return min(dates)
        dates = [e["release_date"][:10] for e in entries]
        if dates:
            return min(dates)
    return detail.get("release_date") or None


def slug(detail):
    """영문 원제에서 안정적인 id 를 만든다.

    한국어/일본어 원제는 ascii 를 거의 남기지 않으므로 (예: "오케이 마담 2" -> "2")
    알파벳이 3자 미만이면 읽기 좋은 id 를 포기하고 tmdb-<id> 로 간다.
    """
    src = detail.get("original_title") or detail.get("title") or ""
    keep = [c.lower() if c.isascii() and c.isalnum() else "-" for c in src]
    s = "".join(keep).strip("-")
    while "--" in s:
        s = s.replace("--", "-")
    s = s[:32].strip("-")
    if sum(c.isalpha() for c in s) < 3:
        return f"tmdb-{detail['id']}"
    return s


def build(detail, today):
    kr = kr_release_date(detail)
    directors = [c["name"] for c in detail.get("credits", {}).get("crew", []) if c.get("job") == "Director"]
    genres = [g["name"] for g in detail.get("genres", [])]
    runtime = detail.get("runtime") or 0

    original = detail.get("release_date") or ""
    original_year = original[:4] if original else ""

    # 화면에는 장르와 러닝타임만 보여준다. 감독·개봉일은 쿠키 유무를 확인하러 온
    # 사람에게 소음이라 숨겼다 — 감독은 나무위키 문서 대조(_directors), 개봉일은
    # 정렬(releaseDate)에 내부적으로만 쓰인다.
    meta = " · ".join(genres[:3]) or "정보 없음"
    meta2 = f"{runtime}분" if runtime else ""

    return {
        "id": slug(detail),
        "tmdbId": detail["id"],
        "title": detail.get("title") or detail.get("original_title"),
        "meta": meta,
        "meta2": meta2,
        "posterPath": detail.get("poster_path"),
        "releaseDate": kr,
        # 박스오피스 TOP 10 에 든 작품만 채워진다.
        "audience": None,
        "boRank": None,
        # 쿠키 정보는 TMDB에 없다 — enrich() 가 채운다.
        "status": "unknown",
        "creditsLen": None,
        "cookies": [],
        "tip": sources.TIP_UNKNOWN,
        "source": "",
        # enrich() 전용, 출력 전에 제거된다.
        "_originalTitle": detail.get("original_title"),
        "_originalYear": original_year,
        "_directors": directors,
        "_keywords": {k["name"] for k in detail.get("keywords", {}).get("keywords", [])},
    }


def enrich(movie):
    """쿠키 정보를 채운다. aftercredits.com → 나무위키 → TMDB 키워드 순.

    어느 쪽도 답하지 않으면 'unknown' 그대로 둔다 — '없음'으로 단정하지 않는다.
    """
    # aftercredits 는 영어 제목으로 색인돼 있다. ko-KR 응답의 title 은 한국어라 못 쓴다.
    try:
        en_title = get(f"/movie/{movie['tmdbId']}", language="en-US").get("title")
    except Exception:
        en_title = None

    year = int(movie["_originalYear"]) if movie["_originalYear"] else None
    hit = sources.aftercredits_lookup(en_title, movie["_originalTitle"], year)

    # 한국·일본 로컬 영화는 영어권 소스에 없다 — 나무위키로 보강.
    if hit is None:
        kr_year = int(movie["releaseDate"][:4]) if movie["releaseDate"] else year
        hit = sources.namu_lookup(movie["title"], kr_year, movie["_directors"])

    if hit is None and movie["_keywords"]:
        kw = movie["_keywords"]
        if sources.KW_AFTER in kw or sources.KW_DURING in kw:
            hit = sources.tmdb_keyword_lookup(movie["tmdbId"], get)

    if hit:
        movie.update({k: v for k, v in hit.items() if k != "matchedTitle"})
    return movie


def main():
    today = datetime.date.today().isoformat()

    ids = []
    for page in PAGES:
        for item in get("/movie/now_playing", region="KR", language="ko-KR", page=page)["results"]:
            if item["id"] not in ids:
                ids.append(item["id"])

    with ThreadPoolExecutor(8) as pool:
        details = list(
            pool.map(
                lambda mid: get(
                    f"/movie/{mid}",
                    language="ko-KR",
                    append_to_response="credits,release_dates,keywords",
                ),
                ids,
            )
        )

    movies = [build(d, today) for d in details]
    # 이미 개봉한 작품만.
    movies = [m for m in movies if m["releaseDate"] and m["releaseDate"] <= today]

    # 직전 피드. 박스오피스 퇴행 방지와 쿠키 판정 이월에 함께 쓴다.
    prev_path = ROOT / "ios" / "data" / "cookies.json"
    prev_feed = json.loads(prev_path.read_text(encoding="utf-8")) if prev_path.exists() else {}
    prev_all = {p["tmdbId"]: p for p in prev_feed.get("movies", [])}

    # 박스오피스 관객수를 붙인다.
    bo_index, bo_date = sources.boxoffice_fetch()
    prev_bo_date = prev_feed.get("boxofficeDate")
    # KOBIS 는 전날 집계를 아침에야 낸다. 그 전에 돌면 하루 더 오래된 집계가
    # 돌아오는데, 그대로 쓰면 관객수와 기준일이 뒤로 간다. 조회에 실패했을 때도
    # 마찬가지다 — 둘 다 직전 집계를 그대로 지킨다.
    stale_bo = bool(prev_bo_date) and (not bo_date or bo_date < prev_bo_date)
    if stale_bo:
        print(f"  박스오피스 {bo_date or '조회 실패'} — 직전({prev_bo_date})보다 오래됨. 직전 집계 유지")
        bo_index, bo_date = {}, prev_bo_date

    for m in movies:
        entry = sources.boxoffice_match(m["title"], bo_index)
        if entry:
            m["audience"] = entry["audience"]
            m["boRank"] = entry["rank"]
        elif stale_bo and (p := prev_all.get(m["tmdbId"])) and p.get("audience") is not None:
            m["audience"] = p["audience"]
            m["boRank"] = p.get("boRank")

    # 최신 개봉순 상위 MAX_MOVIES 편에, 박스오피스 진입작은 개봉일과 무관하게 합집합으로
    # 더한다 — 흥행 중인데 개봉한 지 오래됐다는 이유로 빠지면 박스오피스 목록이 아니다.
    movies.sort(key=lambda m: m["releaseDate"], reverse=True)
    keep = movies[:MAX_MOVIES] + [m for m in movies[MAX_MOVIES:] if m.get("audience")]

    # 관객수 내림차순 — 집계된 작품이 먼저, 나머지는 최신 개봉순으로 뒤에 붙는다.
    keep.sort(key=lambda m: (m.get("audience") is not None, m.get("audience") or 0, m["releaseDate"]), reverse=True)
    movies = keep

    # 쿠키 정보 조회. aftercredits 는 남의 서버라 동시 요청을 3개로 묶어 둔다.
    print(f"쿠키 정보 조회 중… ({len(movies)}편)")
    with ThreadPoolExecutor(3) as pool:
        movies = list(pool.map(enrich, movies))

    # 쿠키 설명 한국어 번역 — 항상 수행한다. 캐시에 있으면 API 없이 즉시,
    # 새 문장은 Claude API(자격증명 있을 때)로, 어느 쪽도 안 되면 영어 원문 유지.
    if "--no-translate" not in sys.argv:
        import translate

        translate.translate_movies(movies)

    # 확인된 쿠키 정보 병합 (tmdbId 기준) — 자동 조회 결과보다 우선한다.
    overrides_path = ROOT / "data.overrides.json"
    overrides = json.loads(overrides_path.read_text(encoding="utf-8")) if overrides_path.exists() else {}
    for m in movies:
        patch = overrides.get(str(m["tmdbId"]))
        if patch:
            m.update(patch)

    # 직전 피드의 확정 판정 이월. 소스가 일시적으로 막혀도(예: GitHub Actions
    # 러너 IP 를 나무위키 Cloudflare 가 차단) 이미 확정된 사실이 '미확인'으로
    # 퇴행하면 안 된다 — 쿠키 유무는 개봉 후 바뀌지 않는 사실이므로, 이번 조회가
    # 답을 못 준 작품만 이전 판정으로 채운다 (새 판정이 있으면 항상 새 것 우선).
    prev = {k: p for k, p in prev_all.items() if p.get("status") in ("yes", "no")}
    carried = 0
    for m in movies:
        if m["status"] == "unknown" and m["tmdbId"] in prev:
            p = prev[m["tmdbId"]]
            m.update({k: p[k] for k in ("status", "cookies", "tip", "creditsLen", "source") if k in p})
            m["sourceUrl"] = p.get("sourceUrl")
            carried += 1
    if carried:
        print(f"  직전 피드에서 판정 이월 {carried}편")

    for m in movies:
        for key in [k for k in m if k.startswith("_")]:
            del m[key]

    body = json.dumps(movies, ensure_ascii=False, indent=2)
    votes = json.dumps({m["id"]: {"up": 0, "down": 0} for m in movies}, ensure_ascii=False, indent=2)
    (ROOT / "data.js").write_text(
        f"""/* 쿠키이써 — 현재 상영작.
   자동 생성 파일입니다. 직접 고치지 말고 `python3 tools/fetch_movies.py` 를 실행하세요.
   작품 정보: TMDB /movie/now_playing?region=KR (조회일 {today})
   관객수: KOBIS 일별 박스오피스 (기준일 {bo_date or '없음'})
   쿠키 정보: aftercredits.com + 나무위키 + TMDB 키워드 + data.overrides.json */

const DATA_UPDATED = '{today}';
const BOXOFFICE_DATE = {json.dumps(bo_date)};

const MOVIES = {body};

const INITIAL_VOTES = {votes};
""",
        encoding="utf-8",
    )
    # iOS 앱 번들용 사본. 웹과 같은 데이터를 쓰되, 앱은 JSON 만 읽으면 되도록 한다.
    ios_data = ROOT / "ios" / "data"
    if ios_data.parent.exists():
        ios_data.mkdir(parents=True, exist_ok=True)
        (ios_data / "cookies.json").write_text(
            json.dumps(
                {"updated": today, "boxofficeDate": bo_date, "movies": movies},
                ensure_ascii=False,
                indent=1,
            ),
            encoding="utf-8",
        )
        print(f"  ios/data/cookies.json 갱신")

    tally = {"yes": 0, "no": 0, "unknown": 0}
    for m in movies:
        tally[m["status"]] = tally.get(m["status"], 0) + 1
    ranked = [m for m in movies if m.get("audience")]
    print(f"\ndata.js 갱신 완료 — {len(movies)}편 (조회일 {today})")
    print(f"  쿠키 있음 {tally['yes']} · 없음 {tally['no']} · 미확인 {tally['unknown']}")
    print(f"  박스오피스 집계 {len(ranked)}편 (기준일 {bo_date or '없음'})")
    for m in ranked:
        print(f"    {m['audience']:>9,}명  {m['title'][:26]:<28} [{m['status']}]")
    for m in movies:
        if m["status"] != "unknown":
            where = ", ".join(c["pos"] for c in m["cookies"]) or "-"
            print(f"    [{m['status']:<7}] {m['title'][:24]:<26} {where:<24} ← {m['source']}")


if __name__ == "__main__":
    main()
