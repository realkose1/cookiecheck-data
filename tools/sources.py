"""쿠키(쿠키 영상) 정보 소스.

TMDB에는 쿠키 데이터가 없어서 여러 소스를 겹쳐 쓴다.

1. aftercredits.com — WordPress REST API 가 공개돼 있고(robots.txt: `Disallow:` 없음)
   본문에 "Are There Any Extras During/After The Credits?" Yes/No 와 스포일러로 감춘
   설명이 구조화돼 있다. **쿠키 '없음'을 단정할 수 있는 유일한 소스.**
   영어권 개봉작 위주라 한국·일본 로컬 영화는 대체로 없다.

2. 나무위키 — 한국·일본 영화는 영어권 소스에 없다. 나무위키는 robots.txt 로
   `/w/`(문서)를 명시 허용하고, 문서 본문이 SSR HTML 에 그대로 들어 있으며,
   국내 개봉작 문서에 쿠키 정보가 자주 서술된다. 다만 자유 서술이라 휴리스틱
   판정이다 — 명확한 신호(목차의 '쿠키 영상' 섹션, "쿠키 영상은 없다" 류의 명시,
   "쿠키 영상에서 ~한다" 서술)가 있을 때만 판정하고, 아니면 미확인으로 남긴다.

3. TMDB 키워드 — `aftercreditsstinger`(179430) / `duringcreditsstinger`(179431).
   붙어 있으면 정확하지만 커버리지가 희박하다. 키워드가 **없다는 것은 근거가 되지
   않으므로**(태깅이 안 됐을 뿐일 수 있다) '있음' 신호로만 쓰고 '없음' 판정에는 쓰지 않는다.

우선순위: data.overrides.json > aftercredits > 나무위키 > TMDB 키워드 > 미확인.
"""

import datetime
import html
import json
import os
import pathlib
import re
import time
import unicodedata
import urllib.parse
import urllib.request

UA = "cookiecheck/0.1 (+personal project; contact via repo)"
AC_API = "https://aftercredits.com/wp-json/wp/v2/posts"

KW_AFTER = "aftercreditsstinger"
KW_DURING = "duringcreditsstinger"

POS_DURING = "크레딧 중간"
POS_AFTER = "크레딧 종료 후"
TIP_NONE = "쿠키가 없습니다. 크레딧이 시작되면 바로 나가셔도 됩니다."
TIP_UNKNOWN = "아직 확인된 제보가 없습니다. 관람하셨다면 알려주세요."


def _get_json(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


# ---------------------------------------------------------------------------
# 제목 정규화 / 매칭
# ---------------------------------------------------------------------------

def normalize_title(s):
    """'Odyssey, The (2026)' 와 'The Odyssey' 가 같은 값이 되도록 정규화."""
    s = unicodedata.normalize("NFKD", s or "").lower()
    s = re.sub(r"\((19|20)\d{2}\)", "", s)
    s = s.strip().rstrip("*").strip()
    s = re.sub(r"^(.*),\s*(the|a|an)$", r"\2 \1", s)  # "Odyssey, The" -> "the odyssey"
    s = re.sub(r"^(the|a|an)\s+", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return s


def _year_in_title(s):
    m = re.search(r"\((19|20)(\d{2})\)", s or "")
    return int(m.group(0)[1:-1]) if m else None


# ---------------------------------------------------------------------------
# aftercredits.com
# ---------------------------------------------------------------------------

def _strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def _parse_extras(content_html):
    """본문에서 during/after 각각의 Yes/No 와 스포일러 설명을 뽑는다.

    구조:
      <p><strong>Are There Any Extras During The Credits? <span>Yes</span></strong></p>
      <div class="spoiler-wrap">
        <div class="spoiler-head folded">Click to see what's during the credits</div>
        <div class="spoiler-body">설명</div>
      </div>

    반환: {'during': (bool|None, desc), 'after': (bool|None, desc)}
    """
    out = {"during": (None, ""), "after": (None, "")}

    # 질문 위치를 먼저 찾고, 그 뒤에 처음 나오는 spoiler-body 를 짝지운다.
    questions = [
        (m.start(), m.group(1).lower(), _strip_tags(m.group(2)))
        for m in re.finditer(
            r"Are There Any Extras (During|After) The Credits\?\s*(.{0,120}?)</strong>",
            content_html,
            re.I | re.S,
        )
    ]
    bodies = [
        (m.start(), _strip_tags(m.group(1)))
        for m in re.finditer(r'<div class="spoiler-body">(.*?)</div>', content_html, re.S)
    ]

    for idx, (pos, which, answer_html) in enumerate(questions):
        answer = _strip_tags(answer_html).lower()
        if "yes" in answer:
            has = True
        elif "no" in answer:
            has = False
        else:
            has = None

        desc = ""
        if has:
            # 이 질문 뒤, 다음 질문 앞에 있는 spoiler-body.
            limit = questions[idx + 1][0] if idx + 1 < len(questions) else len(content_html)
            for bpos, btext in bodies:
                if pos < bpos < limit:
                    desc = btext
                    break
        out[which] = (has, desc)
    return out


# 전송 실패(연결 리셋·타임아웃) 재시도. aftercredits.com 은 개인 WordPress 호스트라
# ThreadPoolExecutor 로 동시에 두드리면 연결 리셋이 드물지 않다 — 그 한 번의 딸꾹질을
# "이 제목은 쿠키가 없다"로 오판하지 않도록 같은 질의를 몇 번 더 두드린다.
AC_RETRIES = 3
AC_BACKOFF = 1.5  # 초, 시도마다 2배

# 재시도까지 다 실패한 질의 문자열. fetch_movies.py 가 실행 끝에 이 값을 읽어
# "aftercredits 조회 실패 N편" 요약을 찍는다. ThreadPoolExecutor 에서 여러 스레드가
# 동시에 append 하지만, CPython 의 list.append 는 원자적이라 별도 락은 필요 없다.
AC_FAILURES = []


def aftercredits_lookup(en_title, original_title, year, session_get=_get_json):
    """제목+연도로 aftercredits 항목을 찾아 쿠키 정보를 반환한다. 없으면 None.

    연도는 반드시 대조한다 — '위커 맨' 처럼 동명 리메이크가 있는 제목에서
    엉뚱한 작품을 붙이지 않기 위해서다 (±1년 허용: 개봉일 표기 차이).
    """
    candidates = [t for t in dict.fromkeys([en_title, original_title]) if t]
    for query in candidates:
        params = urllib.parse.urlencode(
            {"search": query, "per_page": 10, "_fields": "title,link,content,categories"}
        )
        posts = None
        delay = AC_BACKOFF
        for attempt in range(1, AC_RETRIES + 1):
            try:
                posts = session_get(f"{AC_API}?{params}")
                break
            except Exception as e:
                print(f"  aftercredits 조회 실패('{query}'): {e}")
                if attempt < AC_RETRIES:
                    time.sleep(delay)
                    delay *= 2
                else:
                    AC_FAILURES.append(query)
        if posts is None:
            continue

        for post in posts:
            raw_title = _strip_tags(post["title"]["rendered"])
            if normalize_title(raw_title) != normalize_title(query):
                continue
            post_year = _year_in_title(raw_title)
            if year and post_year and abs(post_year - year) > 1:
                continue

            extras = _parse_extras(post["content"]["rendered"])
            during_has, during_desc = extras["during"]
            after_has, after_desc = extras["after"]

            cookies = []
            if during_has:
                cookies.append({"pos": POS_DURING, "len": "", "desc": during_desc})
            if after_has:
                cookies.append({"pos": POS_AFTER, "len": "", "desc": after_desc})

            if cookies:
                status = "yes"
            elif during_has is False and after_has is False:
                status = "no"
            else:
                # 질문 섹션을 못 읽었다 — 카테고리로 최후 판정.
                cats = set(post.get("categories") or [])
                if 6 in cats:      # Non-Stingers
                    status = "no"
                elif 7 in cats:    # Stingers
                    status = "yes"
                else:
                    return None

            return {
                "status": status,
                "cookies": cookies,
                "tip": "" if status == "yes" else (TIP_NONE if status == "no" else TIP_UNKNOWN),
                "source": "aftercredits.com",
                "sourceUrl": post["link"],
                "matchedTitle": raw_title,
            }
    return None


# ---------------------------------------------------------------------------
# 박스오피스 (KOBIS 일별 박스오피스 TOP 10)
# ---------------------------------------------------------------------------
#
# KOBIS 공식 오픈API 를 쓴다 (KOBIS_API_KEY 필요).
#
# 예전에는 남이 공개해 둔 프록시(kukiit.araboke.com)에 붙어 있었다. 데이터 자체는
# KOBIS 공개 정보였지만 허락 없이 남의 서버에 매일 트래픽을 얹는 셈이라 걷어냈다.
#
# 기준일은 '어제'다. KOBIS 는 전날 집계를 아침에 내므로, 아직 안 나왔으면 하루씩
# 뒤로 물러나며 최대 사흘까지 찾는다 — 그래야 새벽에 돌아도 빈손이 되지 않는다.

BOXOFFICE_API = (
    "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
)
BOXOFFICE_LOOKBACK = 3
# 전송 실패(DNS·타임아웃) 재시도. GitHub Actions 러너에서 이름 해석이 간헐적으로
# 무너져 모든 날짜가 한 번에 실패하는 일이 있었다 — 그 한 번의 딸꾹질 때문에
# 집계 전체를 놓치지 않도록 같은 날짜를 몇 번 더 두드린다.
BOXOFFICE_RETRIES = 3
BOXOFFICE_BACKOFF = 1.5  # 초, 시도마다 2배
BOXOFFICE_TIMEOUT = 15


def _bo_norm(title):
    """'오케이 마담 2' 와 '오케이 마담2' 가 같은 값이 되도록."""
    return re.sub(r"[\s:·,\-—()]+", "", (title or "")).lower()


def _boxoffice_request(url, target):
    """한 날짜분 응답. 전송 실패는 **같은 날짜로** 재시도하고, 끝내 실패하면 None.

    '그 날짜에 집계가 없다'(빈 목록)와 '서버에 닿지 못했다'는 전혀 다른 사건이다.
    전자는 하루 앞으로 물러나는 게 맞지만, 후자에서 날짜를 넘기면 멀쩡한 최신
    집계를 스스로 버리고 오래된 날짜로 밀려난다.
    """
    delay = BOXOFFICE_BACKOFF
    for attempt in range(1, BOXOFFICE_RETRIES + 1):
        try:
            return _get_json(url, timeout=BOXOFFICE_TIMEOUT)
        except Exception as e:
            print(f"  KOBIS 요청 실패({target}, 시도 {attempt}/{BOXOFFICE_RETRIES}): {e}")
            if attempt < BOXOFFICE_RETRIES:
                time.sleep(delay)
                delay *= 2
    return None


def boxoffice_fetch():
    """{정규화제목: {title, rank, audience, openDt}} 와 기준일. 실패하면 ({}, None)."""
    key = os.environ.get("KOBIS_API_KEY", "").strip()
    if not key:
        print("  KOBIS_API_KEY 가 없습니다 — 관객수를 건너뜁니다")
        return {}, None

    today = datetime.date.today()
    for back in range(1, BOXOFFICE_LOOKBACK + 1):
        target = (today - datetime.timedelta(days=back)).strftime("%Y%m%d")
        url = f"{BOXOFFICE_API}?key={key}&targetDt={target}"
        data = _boxoffice_request(url, target)
        if data is None:
            # 재시도까지 다 실패했다. 다음 날짜도 같은 이유로 실패할 가능성이 크지만,
            # 하루치 서버 장애일 수도 있으니 마지막 기대로 물러나 본다.
            continue

        # 키가 틀리면 KOBIS 는 HTTP 200 에 faultInfo 를 담아 보낸다 — 조용히
        # 빈손이 되지 않도록 이유를 찍는다.
        fault = data.get("faultInfo")
        if fault:
            print(f"  KOBIS 오류({target}): {fault.get('errorCode')} {fault.get('message')}")
            return {}, None

        items = (data.get("boxOfficeResult") or {}).get("dailyBoxOfficeList") or []
        if not items:
            print(f"  KOBIS {target} 집계 없음 — 하루 앞으로")
            continue

        index = {}
        for item in items:
            index[_bo_norm(item.get("movieNm"))] = {
                # 원제목을 그대로 들고 있어야 TMDB 재검색(boxoffice_tmdb_search)에 쓸 수 있다.
                # 색인 키는 정규화된 값이라 되돌릴 수 없다.
                "title": item.get("movieNm"),
                "rank": _int_or_none(item.get("rank")),
                "audience": _int_or_none(item.get("audiAcc")),
                "openDt": (item.get("openDt") or "").replace("-", "") or None,
            }
        return index, target

    return {}, None


def _int_or_none(v):
    """KOBIS 는 숫자를 문자열로 준다 ("8471045")."""
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def boxoffice_match_key(title, index):
    """제목에 대응하는 색인 키. 부분 일치까지 허용하고, 없으면 None.

    어떤 KOBIS 항목이 **아직 아무 작품에도 안 붙었는지** 알아내려면 값이 아니라
    키가 필요하다 (boxoffice_tmdb_search 로 넘길 미매칭 목록을 만들 때 쓴다).
    """
    key = _bo_norm(title)
    if not key:
        # 빈 제목은 모든 키의 접두사라 아래 루프에서 아무 항목이나 집어온다.
        return None
    if key in index:
        return key
    for other in index:
        if other.startswith(key) or key.startswith(other):
            return other
    return None


def boxoffice_match(title, index):
    """제목으로 박스오피스 항목을 찾는다. 부분 일치까지 허용."""
    key = boxoffice_match_key(title, index)
    return index[key] if key else None


# ---------------------------------------------------------------------------
# KOBIS TOP 10 → TMDB 역검색
# ---------------------------------------------------------------------------
#
# 작품 목록은 TMDB now_playing 에서만 온다. 그래서 TMDB 가 더 이상 상영작으로
# 세지 않는(또는 제목이 안 맞는) KOBIS TOP 10 작품은 앱에서 통째로 사라진다 —
# 실제로 관객수 1·2위가 화면에 없는 날이 있었다. 남은 KOBIS 항목을 제목으로
# 직접 검색해 목록에 되돌려 넣는다.
#
# 다만 **틀린 작품을 1위 자리에 앉히는 것보다 비워 두는 편이 낫다.** 정규화한
# 제목이 맞고 개봉 연도까지 들어맞을 때만 인정하고, 아니면 그 항목은 포기한다.

BOXOFFICE_SEARCH_YEAR_SLACK = 1   # 해외 개봉과 국내 개봉이 해를 넘겨 갈릴 수 있다
BOXOFFICE_SEARCH_MIN_PREFIX = 4   # 접두사 일치를 허용할 최소 길이 ('인턴' 같은 두 글자 제목이 아무 데나 붙지 않도록)

# KOBIS movieNm 에 붙는 부제 꼬리표. TMDB 는 이런 꼬리표를 모르니 검색/비교
# 전에 떼어내야 하는데, 괄호를 통째로 지우면 괄호가 원제목의 일부인 작품까지
# 망가뜨린다 — 그래서 알려진 어휘로만 좁게 매치한다. 전각 숫자·괄호('（４Ｋ）')도
# 섞여 들어오므로 매치 전에 NFKC 로 반각화한다.
_BO_TAG_RE = re.compile(
    r"\(\s*(?:재개봉\d*|더빙|자막|감독판|4k(?:\s*리마스터링)?|imax|확장판)\s*\)\s*$",
    re.IGNORECASE,
)


def _bo_strip_tag(title):
    """(비교/검색용 제목, 꼬리표가 있었는지) 를 돌려준다.

    꼬리표가 없으면 원문 그대로 돌려줘 기존 경로(연도 대조 포함)를 건드리지
    않는다. 꼬리표가 있으면 뒤를 잘라낸 제목을 돌려주는데, 이 경우 호출자는
    연도 대조를 건너뛰어야 한다 — 재개봉·리마스터링판은 KOBIS openDt 가
    재개봉일이라 TMDB release_date(원작 개봉일)와 해가 안 맞기 때문이다.
    """
    raw = title or ""
    norm = unicodedata.normalize("NFKC", raw)
    m = _BO_TAG_RE.search(norm)
    if not m:
        return raw, False
    return norm[:m.start()].rstrip(), True


def _bo_open_date(open_dt):
    """KOBIS openDt('20260729') -> date. 비었거나 형식이 깨졌으면 None."""
    try:
        return datetime.datetime.strptime((open_dt or "").strip(), "%Y%m%d").date()
    except ValueError:
        return None


def _bo_title_score(ko_title, cand):
    """제목 유사도. 2 = 정규화 후 같음, 1 = 한쪽이 다른 쪽의 접두사, 0 = 다름."""
    want = _bo_norm(ko_title)
    want_en = normalize_title(ko_title)
    best = 0
    for raw in (cand.get("title"), cand.get("original_title")):
        got = _bo_norm(raw)
        if not want or not got:
            continue
        if got == want:
            return 2
        # 영문 제목끼리는 관사·구두점까지 털어내는 normalize_title 이 더 정확하다.
        got_en = normalize_title(raw)
        if want_en and got_en and want_en == got_en:
            return 2
        if (got.startswith(want) or want.startswith(got)) and min(len(got), len(want)) >= BOXOFFICE_SEARCH_MIN_PREFIX:
            best = max(best, 1)
    return best


def boxoffice_tmdb_search(ko_title, open_dt, tmdb_get):
    """KOBIS 제목으로 TMDB 작품을 찾는다. 확신이 서는 후보가 없으면 None.

    tmdb_get 은 fetch_movies.get 처럼 (path, **params) 를 받는 호출자다.

    '인턴'(2015, The Intern)과 '인턴'(2026, 국내 영화)처럼 제목이 완전히 같은
    작품이 실재한다 — 제목만으로는 절대 고를 수 없어서 KOBIS 개봉일과 TMDB
    개봉일의 연도를 반드시 대조한다(±1년: 해외 개봉이 해를 넘겨 들어오는 경우).
    KOBIS 개봉일이 없으면 고를 근거가 없으니 포기한다.

    단, '(재개봉)'/'(４K)' 같은 부제 꼬리표가 붙은 제목은 예외다 — 그런 항목의
    KOBIS 개봉일은 재개봉일이라 연도 대조 자체가 성립하지 않는다(_bo_strip_tag
    참고). 이 경로에서는 연도를 대조하는 대신 제목 완전 일치(score 2)만 인정해
    빠진 근거를 메운다: 접두사 일치까지 허용하면 엉뚱한 작품이 1위로 뽑힌다.
    """
    open_date = _bo_open_date(open_dt)
    if not ko_title or not open_date:
        return None

    query_title, has_tag = _bo_strip_tag(ko_title)
    if not query_title:
        return None

    try:
        results = tmdb_get(
            "/search/movie", query=query_title, language="ko-KR", include_adult="false"
        ).get("results") or []
    except Exception as e:
        print(f"  TMDB 검색 실패('{query_title}'): {e}")
        return None

    scored = []
    for cand in results:
        score = _bo_title_score(query_title, cand)
        if not score:
            continue
        if has_tag:
            if score < 2:
                continue  # 연도 근거가 없는 경로라 접두사 일치는 거부한다.
            # 개봉일 근접도는 재개봉일 대 원작 개봉일 비교라 의미가 없다 —
            # 완전 일치 후보들 중에서는 더 알려진(popularity) 쪽을 고른다.
            scored.append(((score, cand.get("popularity") or 0), cand))
            continue
        released = cand.get("release_date") or ""
        try:
            cand_date = datetime.date.fromisoformat(released)
        except ValueError:
            continue  # 개봉일이 없으면 연도 대조를 못 한다 — 근거 부족으로 버린다.
        if abs(cand_date.year - open_date.year) > BOXOFFICE_SEARCH_YEAR_SLACK:
            continue
        gap = abs((cand_date - open_date).days)
        # 제목이 더 정확한 쪽 > 개봉일이 더 가까운 쪽 > 더 알려진 쪽.
        scored.append(((score, -gap, cand.get("popularity") or 0), cand))

    if not scored:
        return None
    return max(scored, key=lambda s: s[0])[1]


# ---------------------------------------------------------------------------
# 나무위키 (한국·일본 영화)
# ---------------------------------------------------------------------------

NAMU_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) cookiecheck/0.1"

# 판정 패턴. 자유 서술이므로 보수적으로 — 확실할 때만 매치되게 좁게 잡는다.
#
# 주의: 본문은 HTML 태그를 벗겨 만들기 때문에 조사 앞뒤에 공백이 끼어들 수 있다
# ("쿠키 <a>영상</a> 이 있다" -> "쿠키 영상 이 있다"). 조사 주변 \s* 를 빼먹으면
# 멀쩡한 서술을 놓친다.
_NAMU_NO = re.compile(r"쿠키\s*(?:영상)?\s*[은는이가]?\s*(?:따로\s*|별도로\s*)?(?:존재하지\s*않|없)")
_NAMU_YES_NARRATIVE = re.compile(r"쿠키\s*영상\s*에서")      # "쿠키 영상에서 ~한다" — 내용 서술 = 존재
_NAMU_YES_EXPLICIT = re.compile(
    r"쿠키\s*영상\s*[이은는가]?\s*(?:총\s*)?(?:[12한두]\s*개\s*)?(?:가\s*)?(?:있|존재|나온|등장)"
)
_NAMU_SECTION = re.compile(r"\d+(?:\.\d+)*\.\s*쿠키\s*(?:영상|등장인물)\s*\[편집\]")  # 목차/헤딩
_NAMU_POS_DURING = re.compile(r"미드\s*크레딧|크레딧\s*중간|엔딩\s*크레딧\s*중|크레딧[이가]?\s*올라가는\s*(?:도중|중간|중)")
_NAMU_POS_AFTER = re.compile(
    r"포스트\s*크레딧|크레딧[이가]?\s*(?:모두|전부|다)?\s*(?:올라간|끝난)\s*(?:후|뒤)"
    r"|크레딧\s*(?:직후|이후)"
)

# 문서가 '쿠키가 있다'까지만 알려주고 내용은 말하지 않을 때 쓰는 설명.
# namu_lookup 과 ko_index_lookup 이 **같은 문장**을 써야 한다 — 색인에서 꺼낸
# 판정과 라이브 조회 결과가 화면에서 달라 보이면 안 되기 때문.
NAMU_DESC_FALLBACK = "쿠키 영상이 있습니다. 자세한 내용은 출처를 확인하세요."


def _namu_fetch_text(title):
    """문서를 받아 태그를 벗긴 본문 텍스트로. 404/오류는 None."""
    url = "https://namu.wiki/w/" + urllib.parse.quote(title)
    req = urllib.request.Request(url, headers={"User-Agent": NAMU_UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            page = r.read().decode("utf-8", "ignore")
    except Exception:
        return None
    text = html.unescape(re.sub(r"<[^>]+>", " ", page))
    return re.sub(r"\s+", " ", text)


def _namu_position(text):
    """쿠키 위치(중간/종료 후)를 판정한다. 못 찾으면 '위치 미확인'.

    위치 패턴을 문서 전체에서 찾으면 안 된다 — 프랜차이즈 문서(코난 시리즈 등)는
    20만 자가 넘고, 다른 작품이나 무관한 문맥의 '크레딧 이후' 를 이 작품의 쿠키
    위치로 오인하게 된다. '쿠키' 언급 주변 창 안에서만 본다.
    """
    windows = [text[max(0, m.start() - 200) : m.start() + 200] for m in re.finditer(r"쿠키", text)]
    for window in windows:
        if _NAMU_POS_DURING.search(window):
            return POS_DURING
        if _NAMU_POS_AFTER.search(window):
            return POS_AFTER
    return "위치 미확인"


def _namu_sentence(text, match_start):
    """매치 지점을 포함한 문장 하나를 설명문으로 다듬어 뽑는다."""
    start = max(text.rfind(". ", 0, match_start), text.rfind("] ", 0, match_start)) + 1
    end = text.find(".", match_start)
    sentence = text[start : end + 1 if end != -1 else match_start + 160]
    sentence = re.sub(r"\[\d+\]|\[편집\]|\[ ?스포일러 ?\]", "", sentence)
    # 태그를 벗기면서 조사 앞에 생긴 공백을 되돌린다 ("영상 이 있다" -> "영상이 있다").
    sentence = re.sub(r"(?<=[가-힣])\s+([이가은는을를에의로]\s)", r"\1", sentence)
    return re.sub(r"\s{2,}", " ", sentence).strip()[:220]


def namu_lookup(ko_title, year, directors):
    """나무위키에서 쿠키 정보를 찾는다. 판정 불가면 None.

    엉뚱한 동명 문서를 붙이지 않도록, 문서 본문에 감독 이름(한국어 표기)이나
    개봉 연도가 실제로 나오는지 확인한 뒤에만 판정한다.
    """
    # 정확 제목 계열. 여기서는 감독 또는 연도 중 하나만 맞아도 그 문서로 인정한다.
    exact = [
        ko_title,
        re.sub(r"\s+(\d+)$", r"\1", ko_title),  # "오케이 마담 2" -> "오케이 마담2"
        f"{ko_title}(영화)",
    ]
    if year:
        exact.append(f"{ko_title}({year}년 영화)")

    # 부제를 떼어낸 계열("위커 맨: 파이널 컷" -> "위커 맨"). 원작·동명이인 문서로
    # 잘못 붙기 쉬우므로 **감독 이름이 본문에 나올 때만** 인정한다.
    base = re.split(r"\s*[:\-–—]\s*", ko_title)[0].strip()
    loose = [base, f"{base}(영화)"] if base and base != ko_title else []

    candidates = [(t, False) for t in dict.fromkeys(exact)] + [(t, True) for t in dict.fromkeys(loose)]

    for title, strict_director in candidates:
        text = _namu_fetch_text(title)
        time.sleep(1.0)  # 남의 서버 — 문서당 1초 간격
        if not text or "해당 문서를 찾을 수 없습니다" in text:
            continue

        director_hit = any(d and d in text for d in directors)
        if strict_director:
            relevant = director_hit
        else:
            relevant = director_hit or (
                year and str(year) in text and ("개봉" in text or "영화" in text)
            )
        if not relevant:
            continue

        url = "https://namu.wiki/w/" + urllib.parse.quote(title)

        if _NAMU_NO.search(text):
            return {
                "status": "no",
                "cookies": [],
                "tip": TIP_NONE,
                "source": "나무위키",
                "sourceUrl": url,
                "matchedTitle": title,
            }

        narrative = _NAMU_YES_NARRATIVE.search(text)
        explicit = _NAMU_YES_EXPLICIT.search(text)
        section = _NAMU_SECTION.search(text)
        if narrative or explicit or section:
            # 목차에 '쿠키 영상' 섹션이 있으면 그것이 근거다 — 서술 문장은 프랜차이즈
            # 문서에서 다른 작품의 쿠키를 가리키는 경우가 있어(코난 시리즈 등) 쓰지 않는다.
            hit = None if section else (explicit or narrative)
            desc = _namu_sentence(text, hit.start()) if hit else NAMU_DESC_FALLBACK
            pos = _namu_position(text)
            return {
                "status": "yes",
                "cookies": [{"pos": pos, "len": "", "desc": desc}],
                "tip": "",
                "source": "나무위키",
                "sourceUrl": url,
                "matchedTitle": title,
            }

        # 이 문서엔 쿠키 신호가 없다. 여기서 멈추지 말고 다음 변형을 계속 본다 —
        # 동명의 다른 문서(예: '호프')가 먼저 걸리면 정작 영화 문서
        # ('호프(영화)')를 못 보고 끝나기 때문이다.
        continue
    return None


def ko_index_lookup(tmdb_id, index):
    """커밋된 나무위키 색인(data/ko-index.json)에서 판정을 꺼낸다. 없으면 None.

    **왜 필요한가.** GitHub Actions 러너 IP 는 나무위키 Cloudflare 에 막혀
    namu_lookup 이 영원히 None 을 돌려준다 — 그래서 한국·일본 영화 쿠키는
    러너에서 절대 채워지지 않는다. 쿠키 유무는 한 번 확정되면 변하지 않는
    사실이므로, 나무위키가 닿는 곳(맥)에서 '발견'한 결과를 색인 파일에 커밋해
    두면 러너는 그 파일만 읽어 '발행'할 수 있다.

    반환 모양은 namu_lookup 과 **같아야 한다** — enrich() 가 둘을 구분 없이
    movie.update() 에 넘기기 때문이다.

    index: sync_namu.py 가 만든 색인 전체 dict ({"entries": {...}, ...}).
           main() 에서 한 번 읽어 넘긴다 (스레드마다 파일을 다시 열지 않도록).
    """
    entry = (index or {}).get("entries", {}).get(str(tmdb_id))
    if not entry:
        return None

    url = entry.get("u") or ""
    status = entry.get("s")

    if status == "no":
        return {
            "status": "no",
            "cookies": [],
            "tip": TIP_NONE,
            "source": "나무위키",
            "sourceUrl": url,
            "matchedTitle": None,
        }
    if status != "yes":
        return None

    # d/a 가 둘 다 0 이면 문서가 '있다'까지만 말한 것 — 위치를 지어내지 않는다.
    positions = []
    if entry.get("d") == 1:
        positions.append(POS_DURING)
    if entry.get("a") == 1:
        positions.append(POS_AFTER)
    if not positions:
        positions = ["위치 미확인"]

    desc = entry.get("t") or NAMU_DESC_FALLBACK
    return {
        "status": "yes",
        # 설명은 문서 서술 한 줄뿐이라 위치별로 쪼개도 같은 문장이 된다
        # (sync_namu.py 가 desc 를 하나만 담는 이유와 같다).
        "cookies": [{"pos": pos, "len": "", "desc": desc} for pos in positions],
        "tip": "",
        "source": "나무위키",
        "sourceUrl": url,
        "matchedTitle": None,
    }


def load_ko_index(path):
    """색인 파일을 읽는다. 없거나 깨졌으면 빈 색인 — 색인이 빠져도 나머지는 돌아야 한다."""
    try:
        data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except Exception:
        return {"entries": {}, "checked": []}
    data.setdefault("entries", {})
    data.setdefault("checked", [])
    return data


# ---------------------------------------------------------------------------
# TMDB 키워드 (보조 — '있음' 신호로만)
# ---------------------------------------------------------------------------

def tmdb_keyword_lookup(tmdb_id, tmdb_get):
    """키워드가 붙어 있으면 쿠키 '있음' 정보를 반환. 없으면 None (= '없음'이 아니라 '모름')."""
    try:
        keywords = {k["name"] for k in tmdb_get(f"/movie/{tmdb_id}/keywords")["keywords"]}
    except Exception:
        return None

    cookies = []
    if KW_DURING in keywords:
        cookies.append({"pos": POS_DURING, "len": "", "desc": "크레딧 중간에 장면이 있습니다."})
    if KW_AFTER in keywords:
        cookies.append({"pos": POS_AFTER, "len": "", "desc": "크레딧이 끝난 뒤 장면이 있습니다."})
    if not cookies:
        return None

    return {
        "status": "yes",
        "cookies": cookies,
        "tip": "",
        "source": "TMDB 키워드",
        "sourceUrl": f"https://www.themoviedb.org/movie/{tmdb_id}",
        "matchedTitle": None,
    }
