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
        try:
            posts = session_get(f"{AC_API}?{params}")
        except Exception:
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


def _bo_norm(title):
    """'오케이 마담 2' 와 '오케이 마담2' 가 같은 값이 되도록."""
    return re.sub(r"[\s:·,\-—()]+", "", (title or "")).lower()


def boxoffice_fetch():
    """{정규화제목: {rank, audience, openDt}} 와 기준일. 실패하면 ({}, None)."""
    key = os.environ.get("KOBIS_API_KEY", "").strip()
    if not key:
        print("  KOBIS_API_KEY 가 없습니다 — 관객수를 건너뜁니다")
        return {}, None

    today = datetime.date.today()
    for back in range(1, BOXOFFICE_LOOKBACK + 1):
        target = (today - datetime.timedelta(days=back)).strftime("%Y%m%d")
        url = f"{BOXOFFICE_API}?key={key}&targetDt={target}"
        try:
            data = _get_json(url)
        except Exception as e:
            print(f"  KOBIS 요청 실패({target}): {e}")
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


def boxoffice_match(title, index):
    """제목으로 박스오피스 항목을 찾는다. 부분 일치까지 허용."""
    key = _bo_norm(title)
    if key in index:
        return index[key]
    for other, entry in index.items():
        if other.startswith(key) or key.startswith(other):
            return entry
    return None


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
            desc = _namu_sentence(text, hit.start()) if hit else "쿠키 영상이 있습니다. 자세한 내용은 출처를 확인하세요."
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
