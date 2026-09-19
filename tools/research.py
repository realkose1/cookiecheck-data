#!/usr/bin/env python3
"""쿠키 '미확인' 작품 자동 조사 — 웹에서 근거를 찾고, 근거가 확실할 때만 기록한다.

사람이 손으로 하던 '미확인 전수조사'를 매일 파이프라인이 대신한다. 작품마다 Claude
한 번을 호출하고, 서버 도구(web_search / web_fetch)로 직접 찾아보게 한 뒤 결과를
data/verdicts-auto.json 에 남긴다. fetch_movies.enrich() 가 다음 회차부터 그 파일을
읽고, 이 스크립트 끝에서 오늘 피드(cookies.json / data.js)도 제자리에서 고친다.

**이 파일의 핵심은 모델이 아니라 그 뒤의 검증이다.** 모델이 "이 URL 에 이렇게
적혀 있다"고 말하면, 파이썬이 그 URL 을 직접 받아 그 문장이 **정말 거기 있는지**
확인한다. 없으면 그 출처는 버린다. 남은 출처가 규칙(아래 STRONG_DOMAINS / 2건 규칙)에
못 미치면 판정을 unknown 으로 강등한다. LLM 이 그럴듯하게 지어낸 인용은 이 단계에서
전부 걸러진다 — 원칙은 '틀린 판정은 없느니만 못하다' 하나다.

사용법:
  export TMDB_READ_TOKEN=...            # 원제·연도·감독을 프롬프트에 넣는 데 쓴다
  python3 tools/research.py             # 최대 RESEARCH_BUDGET 편
  python3 tools/research.py --dry-run   # 모델을 부르지 않고 대상 목록만
  python3 tools/research.py --only 607833   # 한 편만 (재조사 규칙 무시, 검증용)

인증(ANTHROPIC_AUTH_TOKEN / ANTHROPIC_API_KEY)이 없으면 아무 것도 하지 않고
'자동 조사 건너뜀 — 인증 없음' 만 찍고 정상 종료한다.
"""

import argparse
import datetime
import html
import json
import os
import pathlib
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sources  # noqa: E402  (TIP_NONE 등 상수만 쓴다)

ROOT = pathlib.Path(__file__).resolve().parent.parent
FEED_PATH = ROOT / "ios" / "data" / "cookies.json"
DATA_JS_PATH = ROOT / "data.js"
VERDICTS_PATH = ROOT / "data" / "verdicts-auto.json"
OVERRIDES_PATH = ROOT / "data.overrides.json"
REVIEW_PATH = pathlib.Path("/tmp/verdict-review.md")

MODEL = "claude-opus-5"  # translate.py 와 같은 모델을 쓴다

# --- 예산과 재조사 주기 ------------------------------------------------------
# 한 회차에 조사할 작품 수. 비용 상한이자 남의 서버(검색 대상 사이트)에 대한
# 배려다. 미확인이 10편이어도 오늘 6편, 내일 나머지 — 쿠키 유무는 급한 정보가
# 아니고, 하루 이틀 늦게 채워도 틀린 것보다 낫다.
RESEARCH_BUDGET = 6

# 판정(yes/no)이 한 번 나오면 다시 조사하지 않는다. 쿠키 유무는 개봉 후 변하지
# 않는 사실이라 재조사에 돈을 쓸 이유가 없다 (틀렸다면 data.overrides.json 으로
# 사람이 고친다 — override 가 항상 이긴다).
#
# 'unknown' 으로 끝난 작품만 다시 본다. 개봉 직후에는 아직 아무도 안 썼다가
# 며칠 뒤 리뷰가 올라오는 일이 흔하기 때문이다. 다만 영원히 두드리면 예산을
# 전부 잡아먹으므로 두 개의 문을 둔다.
RETRY_UNKNOWN_DAYS = 3   # unknown 기록은 3일에 한 번만 다시 시도
GIVE_UP_AFTER_DAYS = 60  # 개봉 60일이 지나도록 자료가 없으면 앞으로도 안 나온다

# --- 모델 호출 --------------------------------------------------------------
MAX_SEARCHES = 8   # 작품 하나에 허용하는 웹 검색 횟수
MAX_FETCHES = 6    # 작품 하나에 허용하는 페이지 열람 횟수
MAX_TOKENS = 8000
MAX_PAUSE_RESUMES = 3  # 서버 도구 루프가 pause_turn 으로 끊길 때 이어 붙일 횟수

# 서버 도구 타입은 모델/SDK 세대마다 이름이 다르다. 최신형(동적 필터링)을 먼저
# 시도하고, API 가 모르는 타입이라고 거절하면 구형으로 한 번 물러선다. 러너의
# `pip install anthropic` 이 어느 버전을 깔든 이 목록 중 하나는 통한다.
TOOL_VARIANTS = [
    ("web_search_20260209", "web_fetch_20260209"),
    ("web_search_20250305", "web_fetch_20250910"),
]
_tool_variant = None  # 한 번 통한 조합을 기억해 두 번 실패하지 않는다

# --- 검증 -------------------------------------------------------------------
VERIFY_UA = (
    "Mozilla/5.0 (compatible; cookiecheck-verify/0.1; "
    "+personal project; contact via repo)"
)
VERIFY_TIMEOUT = 20
QUOTE_MIN_CHARS = 20  # 이보다 짧은 인용은 우연히 일치할 수 있어 근거로 안 친다
VERIFY_MAX_BYTES = 4_000_000

# 이 도메인 하나만으로 판정을 인정한다. 쿠키 유무를 본업으로 다루거나(앞의 둘),
# 편집 이력이 남아 대조가 가능한 곳(나무위키), 또는 취재된 보도다.
STRONG_DOMAINS = {"aftercredits.com", "mediastinger.com", "namu.wiki"}

# 언론사. 완벽한 목록일 필요는 없다 — 여기 없으면 '2건 규칙'으로 떨어질 뿐이고,
# 그 방향의 실수는 판정을 못 하는 쪽(안전한 쪽)이다.
NEWS_DOMAINS = {
    "yna.co.kr", "news1.kr", "newsis.com", "chosun.com", "donga.com",
    "joongang.co.kr", "hani.co.kr", "khan.co.kr", "mk.co.kr", "mt.co.kr",
    "hankyung.com", "sedaily.com", "edaily.co.kr", "seoul.co.kr",
    "kmib.co.kr", "segye.com", "munhwa.com", "hankookilbo.com",
    "ytn.co.kr", "sbs.co.kr", "imbc.com", "kbs.co.kr", "jtbc.co.kr",
    "osen.co.kr", "sportschosun.com", "sportsseoul.com", "spotvnews.co.kr",
    "tvreport.co.kr", "xportsnews.com", "newspim.com", "gukjenews.com",
    "ggilbo.com", "etoday.co.kr", "topstarnews.net", "cine21.com",
    "variety.com", "hollywoodreporter.com", "slashfilm.com", "screenrant.com",
    "collider.com", "empireonline.com", "ign.com", "polygon.com",
    "thewrap.com", "deadline.com", "ew.com", "cbr.com", "gamesradar.com",
    "digitalspy.com", "radiotimes.com", "denofgeek.com",
}

# 운영자가 API 를 잠근 사이트다. 인용도 하지 않는다.
BANNED_DOMAINS = {"kukiit.co.kr"}

# 화면에 보이는 출처 이름. 목록에 없으면 도메인을 그대로 쓴다.
SITE_LABELS = {
    "namu.wiki": "나무위키",
    "aftercredits.com": "aftercredits.com",
    "mediastinger.com": "mediastinger.com",
}

# --- 비용 추정 (대략) --------------------------------------------------------
# 로그에 "대략"이라고 찍는 이유: 캐시 적중·서버 도구 내부 토큰까지는 세지 않는다.
# 단가가 바뀌면 여기만 고치면 된다.
PRICE_IN_PER_MTOK = 5.00     # claude-opus-5 입력 $/1M tokens
PRICE_OUT_PER_MTOK = 25.00   # claude-opus-5 출력 $/1M tokens
PRICE_SEARCH_PER_1K = 10.00  # 웹 검색 $/1,000회 (web_fetch 는 현재 과금 없음)

VALID_POS = ("크레딧 중간", "크레딧 종료 후", "위치 미확인")

SYSTEM = """너는 영화의 '쿠키 영상'(post-credits / mid-credits scene) 유무를 확인하는 조사원이다.
한국 앱 '쿠키이써'가 쓸 판정을 만든다. 이 앱의 원칙은 하나다 — **틀린 판정은 없느니만 못하다.**

## 목표
채우는 게 목표가 아니다. **맞는 것만 채우는 게** 목표다. 못 찾으면 unknown 이 정답이고,
unknown 은 실패가 아니다. 억지로 yes/no 를 만들어내는 것이 유일한 실패다.

## 근거 규칙
- 근거 없이 추측하지 마라. 웹에서 실제로 읽은 문장만 근거다.
- **'없음'도 '있음'만큼 명시적인 근거가 필요하다.** "쿠키 언급을 찾지 못했다"는 '없음'의
  근거가 아니다. 누군가 "쿠키 없음", "쿠키 영상은 없다", "no post-credits scene",
  "there is no scene after the credits" 라고 **적어 놓은 문장을 찾아야** '없음'이다.
  못 찾았으면 no 가 아니라 unknown 이다.
- 관례는 근거가 아니다. "마블/프랜차이즈니까 있을 것이다", "일본 애니는 보통 있다",
  "요즘 영화는 대개 있다" — 전부 근거가 아니다. 이런 추론으로 판정하지 마라.
- 관객 후기·개인 블로그·커뮤니티 글은 **서로 독립된 출처 2건 이상이 일치할 때만** 근거다.
  (같은 글을 퍼 나른 두 페이지는 1건이다.)
- aftercredits.com, mediastinger.com, 나무위키(namu.wiki), 언론 보도는 1건으로 충분하다.
- **kukiit.co.kr 은 절대 사용하지도, 인용하지도 마라.** 검색 결과에 나와도 열지 말고 무시해라.
- 동명 작품에 주의해라. 예: 2026년 한국 영화 '인턴'과 2015년 미국 영화 'The Intern'은
  다른 작품이다. **연도와 감독이 일치하는지 반드시 확인**하고, 확인이 안 되면 그 출처는 버려라.

## 검색 요령
- 국내 영화·국내 개봉 정보는 한국어로 검색해라 ("<제목> 쿠키", "<제목> 쿠키영상", "<제목> 엔딩크레딧").
- 해외 작품은 영문 원제로도 검색해라 ("<original title> post credits scene", "<original title> after credits").
- 근거가 될 문장을 찾으면 그 페이지를 web_fetch 로 직접 열어 문장을 **그대로** 확인해라.

## 인용문 (가장 중요)
sources 의 quote 는 **그 페이지 본문에 글자 그대로 존재하는 문장**이어야 한다.
요약·번역·재구성·말줄임 금지. 20자 이상이어야 한다. 검증 프로그램이 그 URL 을 직접 받아
문장이 실제로 있는지 대조하고, 없으면 그 출처를 버린다. 지어낸 인용은 아무 도움이 안 되며
판정 전체를 unknown 으로 떨어뜨린다. 확신이 없으면 그 출처를 넣지 마라.

## 출력
설명·머리말·코드펜스 없이 **JSON 객체 하나만** 출력해라.

{"status":"yes"|"no"|"unknown",
 "cookies":[{"pos":"크레딧 중간"|"크레딧 종료 후"|"위치 미확인","desc":"한국어 1~3문장"}],
 "sources":[{"url":"...","quote":"페이지에 실제로 있는 문장 그대로, 20자 이상"}],
 "reason":"왜 이 판정인지 한 줄"}

- status 가 "no" 거나 "unknown" 이면 cookies 는 빈 배열이다.
- status 가 "unknown" 이면 sources 는 비어 있어도 된다.
- desc 는 한국어로 쓴다. 스포일러를 흐리지 말고 있는 그대로 적는다(앱이 가려서 보여준다)."""


# ---------------------------------------------------------------------------
# 유틸
# ---------------------------------------------------------------------------

def _load_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def domain_of(url):
    """호스트명에서 www. 를 떼고 소문자로. 판별이 안 되면 빈 문자열."""
    try:
        host = urllib.parse.urlsplit(url).hostname or ""
    except ValueError:
        return ""
    host = host.lower()
    return host[4:] if host.startswith("www.") else host


def is_banned(url):
    d = domain_of(url)
    return any(d == b or d.endswith("." + b) for b in BANNED_DOMAINS)


def _domain_in(d, group):
    return any(d == g or d.endswith("." + g) for g in group)


def site_label(url):
    d = domain_of(url)
    return SITE_LABELS.get(d, d or "웹")


def normalize_text(s):
    """인용문 대조를 위한 정규화. 본문과 인용문에 **똑같이** 적용해야 한다.

    같은 문장이 페이지에서는 전각 따옴표에 줄바꿈이 섞여 있고 모델 응답에서는
    반각 따옴표 한 줄로 오는 일이 흔하다. 그 차이 때문에 멀쩡한 근거를 버리면
    자동 조사가 통째로 무력해지므로, 의미를 바꾸지 않는 표기 차이는 지운다.
    """
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("​", "").replace("﻿", "").replace("\xad", "")
    for ch in "‘’ʼ′`´":
        s = s.replace(ch, "'")
    for ch in "“”″「」":
        s = s.replace(ch, '"')
    for ch in "‐‑‒–—―−":
        s = s.replace(ch, "-")
    s = s.replace("…", "...")
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def _aftercredits_body(url):
    """aftercredits.com 글의 본문을 WP JSON API 로 따로 받아 온다.

    그 사이트는 기사 본문을 렌더된 HTML 에 싣지 않아서(내려받으면 메뉴와 태그만
    나온다), 인용문 대조가 늘 실패한다. 멀쩡한 근거를 표기 방식 때문에 버리는
    셈이라, 같은 글을 API 에서 한 번 더 받아 본문에 덧댄다. sources.py 가 이미
    쓰는 바로 그 엔드포인트다 (상수만 빌려 온다).
    """
    slug = urllib.parse.urlsplit(url).path.strip("/").rsplit("/", 1)[-1]
    if not slug:
        return ""
    api = f"{sources.AC_API}?slug={urllib.parse.quote(slug)}"
    req = urllib.request.Request(api, headers={"User-Agent": VERIFY_UA, "accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=VERIFY_TIMEOUT) as r:
            posts = json.load(r)
    except Exception:
        return ""
    parts = []
    for p in posts if isinstance(posts, list) else []:
        for field in ("title", "content", "excerpt"):
            parts.append((p.get(field) or {}).get("rendered") or "")
    return html.unescape(re.sub(r"<[^>]+>", " ", " ".join(parts)))


def page_text(url):
    """페이지를 받아 태그를 벗긴 본문 텍스트로. 실패하면 (None, 사유)."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": VERIFY_UA,
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            "Accept-Language": "ko,en;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=VERIFY_TIMEOUT) as r:
            raw = r.read(VERIFY_MAX_BYTES)
            charset = r.headers.get_content_charset() or "utf-8"
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception as e:  # DNS, 타임아웃, TLS 등
        return None, type(e).__name__

    page = raw.decode(charset, "ignore")
    # script/style 안의 코드가 본문으로 섞이면 엉뚱한 문자열이 '포함'될 수 있다.
    page = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", page)
    text = html.unescape(re.sub(r"<[^>]+>", " ", page))
    if _domain_in(domain_of(url), {"aftercredits.com"}):
        text += " " + _aftercredits_body(url)
    return text, None


# ---------------------------------------------------------------------------
# 대상 선정
# ---------------------------------------------------------------------------

def _days_since(iso_date, today):
    try:
        d = datetime.date.fromisoformat(iso_date[:10])
    except (TypeError, ValueError):
        return None
    return (today - d).days


def select_targets(movies, verdicts, overrides, today, budget=RESEARCH_BUDGET, verbose=True):
    """조사할 작품을 고른다. 로그를 남기며 거르고, 박스오피스 순위 순으로 자른다."""
    picked = []
    for m in movies:
        if m.get("status") != "unknown":
            continue
        key = str(m["tmdbId"])

        # 사람이 data.overrides.json 에 손을 댄 작품은 건드리지 않는다. override 는
        # 언제나 자동 판정을 이기므로 조사해 봐야 화면에 반영되지 않고, 사람이
        # '자료가 없더라'고 확인해 둔 작품일 수도 있다.
        if key in overrides:
            if verbose:
                print(f"  건너뜀 {m['title'][:20]} — data.overrides.json 에 사람 판정이 있음")
            continue

        rec = verdicts.get(key)
        if rec:
            if rec.get("status") in ("yes", "no"):
                continue  # 확정된 사실은 다시 묻지 않는다
            age = _days_since(rec.get("checkedAt", ""), today)
            if age is not None and age < RETRY_UNKNOWN_DAYS:
                continue
            since_release = _days_since(m.get("releaseDate") or "", today)
            if since_release is not None and since_release > GIVE_UP_AFTER_DAYS:
                if verbose:
                    print(f"  건너뜀 {m['title'][:20]} — 개봉 {since_release}일 경과, 재조사 중단")
                continue
        picked.append(m)

    # 박스오피스 순위가 있는 작품 먼저. 많이 보는 영화의 '미확인'이 가장 아프다.
    picked.sort(key=lambda m: (m.get("boRank") or 999, m.get("releaseDate") or "", m["title"]))
    return picked[:budget]


# ---------------------------------------------------------------------------
# TMDB 보강 — 프롬프트에 넣을 원제·연도·감독
# ---------------------------------------------------------------------------

def tmdb_context(tmdb_id):
    """원제·원 개봉연도·감독·영문 제목. 토큰이 없거나 실패하면 빈 dict."""
    try:
        import fetch_movies  # TMDB_READ_TOKEN 이 없으면 import 중 SystemExit
    except SystemExit:
        print("  TMDB_READ_TOKEN 이 없어 원제·감독 없이 조사합니다 (동명 작품 오인 위험 ↑)")
        return {}
    except Exception:
        return {}
    try:
        detail = fetch_movies.get(f"/movie/{tmdb_id}", language="en-US", append_to_response="credits")
    except Exception as e:
        print(f"  TMDB 조회 실패 (#{tmdb_id}): {type(e).__name__}")
        return {}
    return {
        "englishTitle": detail.get("title"),
        "originalTitle": detail.get("original_title"),
        "originalLanguage": detail.get("original_language"),
        "year": (detail.get("release_date") or "")[:4],
        "directors": [c["name"] for c in detail.get("credits", {}).get("crew", []) if c.get("job") == "Director"],
    }


def build_prompt(movie, ctx):
    lines = [
        f"한국 제목: {movie['title']}",
        f"TMDB id: {movie['tmdbId']}",
    ]
    if ctx.get("originalTitle"):
        lines.append(f"원제: {ctx['originalTitle']}")
    if ctx.get("englishTitle") and ctx.get("englishTitle") != ctx.get("originalTitle"):
        lines.append(f"영문 제목: {ctx['englishTitle']}")
    if ctx.get("year"):
        lines.append(f"제작/원 개봉 연도: {ctx['year']}")
    if movie.get("releaseDate"):
        lines.append(f"국내 개봉일: {movie['releaseDate']}")
    if ctx.get("directors"):
        lines.append(f"감독: {', '.join(ctx['directors'])}")
    if movie.get("meta"):
        lines.append(f"장르: {movie['meta']}")
    lines.append(
        "\n이 작품에 쿠키 영상이 있는지 조사해라. 연도와 감독으로 동명 작품을 반드시 배제해라."
        " 근거를 못 찾으면 unknown 으로 답해라. JSON 하나만 출력해라."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 모델 호출
# ---------------------------------------------------------------------------

def _extract_json(text):
    """응답 텍스트에서 JSON 객체 하나를 꺼낸다. 실패하면 None.

    서버 도구를 쓰면 텍스트 블록이 여러 개로 쪼개지고 앞뒤에 설명이 붙기도 한다.
    그래서 '마지막 중괄호 덩어리'를 괄호 균형으로 직접 찾는다.
    """
    if not text:
        return None
    text = re.sub(r"```(?:json)?|```", "", text)
    depth = end = -1
    for i in range(len(text) - 1, -1, -1):
        c = text[i]
        if c == "}":
            if depth < 0:
                depth, end = 0, i
            depth += 1
        elif c == "{" and depth > 0:
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[i : end + 1])
                except json.JSONDecodeError:
                    depth, end = -1, -1
    return None


def call_model(client, movie, ctx):
    """작품 하나를 조사시킨다. (결과 dict | None, usage dict) 를 돌려준다."""
    global _tool_variant
    import anthropic

    usage = {"in": 0, "out": 0, "searches": 0}
    variants = [_tool_variant] if _tool_variant else list(TOOL_VARIANTS)

    for search_type, fetch_type in variants:
        tools = [
            {"type": search_type, "name": "web_search", "max_uses": MAX_SEARCHES},
            {"type": fetch_type, "name": "web_fetch", "max_uses": MAX_FETCHES},
        ]
        messages = [{"role": "user", "content": build_prompt(movie, ctx)}]
        try:
            for _ in range(MAX_PAUSE_RESUMES + 1):
                resp = client.messages.create(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    system=SYSTEM,
                    messages=messages,
                    tools=tools,
                )
                u = getattr(resp, "usage", None)
                if u:
                    usage["in"] += getattr(u, "input_tokens", 0) or 0
                    usage["out"] += getattr(u, "output_tokens", 0) or 0
                    stu = getattr(u, "server_tool_use", None)
                    usage["searches"] += (getattr(stu, "web_search_requests", 0) or 0) if stu else 0
                # 서버 도구 루프가 한도에 닿으면 pause_turn 으로 끊긴다. 응답을
                # 그대로 되돌려 보내면 서버가 이어서 계속한다 ("계속해" 같은 말을
                # 덧붙이면 안 된다).
                if getattr(resp, "stop_reason", None) != "pause_turn":
                    break
                messages = messages + [{"role": "assistant", "content": resp.content}]
            _tool_variant = (search_type, fetch_type)
            text = "\n".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
            return _extract_json(text), usage
        except anthropic.BadRequestError as e:
            msg = str(e)
            if search_type in msg or fetch_type in msg or "tool" in msg.lower():
                print(f"  서버 도구 {search_type} 거절됨 — 이전 세대 타입으로 재시도")
                continue
            print(f"  모델 호출 실패: BadRequestError: {msg[:200]}")
            return None, usage
        except Exception as e:
            print(f"  모델 호출 실패: {type(e).__name__}: {str(e)[:200]}")
            return None, usage
    print("  서버 도구 타입을 하나도 쓰지 못했습니다 — SDK/모델 조합을 확인하세요")
    return None, usage


# ---------------------------------------------------------------------------
# 결정적 검증 — 여기가 안전장치다
# ---------------------------------------------------------------------------

def verify_sources(raw_sources, log=print):
    """모델이 준 출처를 하나씩 직접 받아 인용문을 대조한다.

    돌려주는 값: (통과한 출처 리스트, 탈락 사유 리스트)
    통과한 출처는 {"url","quote","domain","strong"} 형태다.
    """
    kept, dropped = [], []
    seen = set()
    for s in raw_sources or []:
        url = (s or {}).get("url") or ""
        quote = (s or {}).get("quote") or ""
        if not url.startswith(("http://", "https://")):
            dropped.append(f"{url[:60] or '(빈 URL)'}: URL 아님")
            continue
        if is_banned(url):
            # 운영자가 막아 둔 사이트다. 받지도 않고 버린다.
            log(f"      ⚠ 금지 출처 인용 시도 — 폐기: {url[:80]}")
            dropped.append(f"{domain_of(url)}: 사용 금지 사이트")
            continue
        if url in seen:
            continue
        seen.add(url)

        norm_quote = normalize_text(quote)
        if len(norm_quote) < QUOTE_MIN_CHARS:
            dropped.append(f"{domain_of(url)}: 인용문이 {QUOTE_MIN_CHARS}자 미만")
            continue

        text, err = page_text(url)
        if text is None:
            dropped.append(f"{domain_of(url)}: 페이지를 받지 못함 ({err})")
            continue
        if norm_quote not in normalize_text(text):
            dropped.append(f"{domain_of(url)}: 인용문이 페이지에 없음")
            continue

        d = domain_of(url)
        kept.append({
            "url": url,
            "quote": quote.strip(),
            "domain": d,
            "strong": _domain_in(d, STRONG_DOMAINS) or _domain_in(d, NEWS_DOMAINS),
        })
    return kept, dropped


def evidence_ok(kept):
    """검증을 통과한 출처가 판정을 뒷받침하기에 충분한가.

    강한 출처(쿠키 전문 사이트·나무위키·언론)는 1건, 그 밖(후기·블로그·커뮤니티)은
    서로 다른 도메인 2건. 목록에 없는 언론사가 2건 규칙으로 떨어지는 건
    괜찮다 — 그 방향의 실수는 판정을 못 하는 쪽이다.
    """
    if any(s["strong"] for s in kept):
        return True, ""
    domains = {s["domain"] for s in kept}
    if len(domains) >= 2:
        return True, ""
    if not kept:
        return False, "검증을 통과한 출처가 없음"
    return False, f"독립 출처 1건뿐 ({', '.join(domains)}) — 후기·블로그는 2건 필요"


def normalize_cookies(raw, status):
    if status != "yes":
        return []
    out = []
    for c in raw or []:
        if not isinstance(c, dict):
            continue
        pos = c.get("pos") if c.get("pos") in VALID_POS else "위치 미확인"
        desc = (c.get("desc") or "").strip()
        out.append({"pos": pos, "len": "", "desc": desc})
    return out or [{"pos": "위치 미확인", "len": "", "desc": "쿠키 영상이 있습니다. 자세한 내용은 출처를 확인하세요."}]


def make_record(result, kept, today):
    """검증을 통과한 근거로 verdicts-auto.json 에 넣을 기록을 만든다."""
    status = result.get("status")
    label = " · ".join(dict.fromkeys(site_label(s["url"]) for s in kept[:2]))
    return {
        "status": status,
        "cookies": normalize_cookies(result.get("cookies"), status),
        # '없음'일 때만 안내 문구를 넣는다. '있음'은 cookies 가 화면을 채운다.
        "tip": sources.TIP_NONE if status == "no" else "",
        # 화면에서 자동 판정임이 보여야 한다. 사람이 "이건 누가 확인한 거지?"
        # 하고 물을 수 있어야 검토 루프가 돈다.
        "source": f"{label} (자동 조사)",
        "sourceUrl": kept[0]["url"],
        "quote": kept[0]["quote"],
        "checkedAt": today,
        "model": MODEL,
        "reason": (result.get("reason") or "").strip()[:200],
    }


# ---------------------------------------------------------------------------
# 제자리 패치 — 오늘 피드에 바로 반영
# ---------------------------------------------------------------------------

PATCH_FIELDS = ("status", "cookies", "tip", "source", "sourceUrl")


def _patch_movie(movie, rec):
    movie.update({k: rec[k] for k in PATCH_FIELDS if k in rec})


def patch_feed(verdicts, overrides):
    """cookies.json 과 data.js 의 미확인 작품을 자동 판정으로 덮는다.

    research.py 는 fetch_movies.py **뒤에** 돈다 (오늘 피드의 미확인을 보고
    조사하니까). 그대로 두면 판정이 내일 피드에나 실린다. fetch_movies 를 한 번
    더 돌리면 TMDB·aftercredits 를 두 번 두드리게 되므로, override 병합과 같은
    방식으로 두 파일을 제자리에서 고친다.

    override 가 있는 작품은 건드리지 않는다 — override 가 최종 권위다.
    """
    usable = {k: v for k, v in verdicts.items() if v.get("status") in ("yes", "no")}
    if not usable:
        return 0

    patched = set()

    feed = _load_json(FEED_PATH, None)
    if feed and isinstance(feed.get("movies"), list):
        for m in feed["movies"]:
            key = str(m.get("tmdbId"))
            if key in overrides or m.get("status") != "unknown" or key not in usable:
                continue
            _patch_movie(m, usable[key])
            patched.add(key)
        if patched:
            FEED_PATH.write_text(
                json.dumps(feed, ensure_ascii=False, indent=1), encoding="utf-8"
            )

    if DATA_JS_PATH.exists():
        js = DATA_JS_PATH.read_text(encoding="utf-8")
        m = re.search(r"(?s)(const MOVIES = )(\[.*?\n\];)", js)
        if m:
            try:
                movies = json.loads(m.group(2)[:-1])
            except json.JSONDecodeError:
                movies = None
            if movies is not None:
                hit = False
                for mv in movies:
                    key = str(mv.get("tmdbId"))
                    if key in overrides or mv.get("status") != "unknown" or key not in usable:
                        continue
                    _patch_movie(mv, usable[key])
                    hit = True
                if hit:
                    body = json.dumps(movies, ensure_ascii=False, indent=2)
                    DATA_JS_PATH.write_text(
                        js[: m.start(2)] + body + ";" + js[m.end(2):], encoding="utf-8"
                    )

    return len(patched)


# ---------------------------------------------------------------------------
# 사람 검토용 기록
# ---------------------------------------------------------------------------

def write_review(new_records, path=REVIEW_PATH):
    """새로 생긴 자동 판정을 사람이 훑어볼 수 있는 마크다운으로 남긴다.

    워크플로가 이 파일을 GitHub 이슈로 올린다. 틀린 게 보이면 사용자가
    data.overrides.json 으로 고친다 — override 가 항상 이기므로 그걸로 끝이다.
    """
    if not new_records:
        if path.exists():
            path.unlink()
        return
    mark = {"yes": "🍪 있음", "no": "🚫 없음"}
    lines = []
    for title, rec in new_records:
        lines.append(f"### {title} — {mark.get(rec['status'], rec['status'])}")
        lines.append("")
        lines.append(f"- 출처: {rec['source']}")
        lines.append(f"- URL: {rec['sourceUrl']}")
        lines.append(f"- 인용: “{rec['quote']}”")
        lines.append(f"- 근거 요약: {rec['reason']}")
        for c in rec.get("cookies", []):
            lines.append(f"- 쿠키: [{c['pos']}] {c['desc']}")
        lines.append("")
    lines.append("---")
    lines.append("틀린 판정이 있으면 `data.overrides.json` 에서 고쳐 주세요 — override 가 항상 이깁니다.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def have_credentials():
    return bool(
        os.environ.get("ANTHROPIC_AUTH_TOKEN", "").strip()
        or os.environ.get("ANTHROPIC_API_KEY", "").strip()
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description="미확인 작품 쿠키 자동 조사")
    ap.add_argument("--dry-run", action="store_true", help="모델을 부르지 않고 대상 목록만 찍는다")
    ap.add_argument("--only", type=str, default=None, help="이 tmdbId 한 편만 조사한다 (재조사 규칙 무시)")
    ap.add_argument("--budget", type=int, default=RESEARCH_BUDGET)
    args = ap.parse_args(argv)

    today = datetime.date.today().isoformat()
    feed = _load_json(FEED_PATH, {})
    movies = feed.get("movies", [])
    if not movies:
        print(f"자동 조사 건너뜀 — 피드가 없습니다 ({FEED_PATH})")
        return 0

    verdicts = _load_json(VERDICTS_PATH, {})
    overrides = {k: v for k, v in _load_json(OVERRIDES_PATH, {}).items() if not k.startswith("_")}

    if args.only:
        targets = [m for m in movies if str(m.get("tmdbId")) == args.only]
        if not targets:
            print(f"--only {args.only} — 피드에 없는 tmdbId 입니다")
            return 1
    else:
        targets = select_targets(movies, verdicts, overrides, datetime.date.today(),
                                 budget=args.budget)

    if not targets:
        print("자동 조사 대상 없음 — 미확인 작품이 없거나 모두 최근에 조사했습니다")
        return 0

    print(f"자동 조사 대상 {len(targets)}편 (미확인 {sum(1 for m in movies if m.get('status') == 'unknown')}편 중):")
    for m in targets:
        rank = f"BO {m['boRank']}위" if m.get("boRank") else "순위 없음"
        print(f"  #{m['tmdbId']:<9} {m['title'][:24]:<26} {rank:<10} 개봉 {m.get('releaseDate')}")
    if args.dry_run:
        print("\n--dry-run — 모델을 부르지 않고 끝냅니다")
        return 0

    if not have_credentials():
        # 조용히 빠지지 않는다. 몇 주 동안 말없이 아무 것도 안 하는 게 최악이다.
        print("자동 조사 건너뜀 — 인증 없음 (ANTHROPIC_AUTH_TOKEN / ANTHROPIC_API_KEY)")
        return 0

    try:
        import anthropic
    except ImportError:
        print("자동 조사 건너뜀 — pip install anthropic 이 필요합니다")
        return 0
    client = anthropic.Anthropic()

    tally = {"yes": 0, "no": 0, "unknown": 0}
    demoted = 0
    total = {"in": 0, "out": 0, "searches": 0}
    new_records = []

    for m in targets:
        key = str(m["tmdbId"])
        print(f"\n▸ {m['title']} (#{key})")
        ctx = tmdb_context(m["tmdbId"])
        result, usage = call_model(client, m, ctx)
        for k in total:
            total[k] += usage[k]

        if not result or result.get("status") not in ("yes", "no", "unknown"):
            reason = "모델 응답을 해석하지 못함"
            verdicts[key] = {"status": "unknown", "checkedAt": today, "reason": reason}
            tally["unknown"] += 1
            print(f"    [unknown] {reason}")
            continue

        status = result["status"]
        if status == "unknown":
            reason = (result.get("reason") or "근거를 찾지 못함").strip()[:200]
            verdicts[key] = {"status": "unknown", "checkedAt": today, "reason": reason}
            tally["unknown"] += 1
            print(f"    [unknown] {reason}")
            continue

        kept, dropped = verify_sources(result.get("sources"), log=print)
        for d in dropped:
            print(f"      검증 탈락 — {d}")
        ok, why = evidence_ok(kept)
        if not ok:
            # 판정을 지우고 unknown 으로 내린다. 모델이 yes 라고 했어도,
            # 파이썬이 눈으로 확인하지 못한 판정은 기록하지 않는다.
            reason = f"'{status}' 로 답했으나 근거 부족 — {why}"
            verdicts[key] = {"status": "unknown", "checkedAt": today, "reason": reason}
            tally["unknown"] += 1
            demoted += 1
            print(f"    [강등→unknown] {reason}")
            continue

        rec = make_record(result, kept, today)
        verdicts[key] = rec
        tally[status] += 1
        new_records.append((m["title"], rec))
        print(f"    [{status}] {rec['source']} — {rec['sourceUrl']}")
        print(f"      인용: {rec['quote'][:100]}")

    VERDICTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERDICTS_PATH.write_text(
        json.dumps(verdicts, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8"
    )
    write_review(new_records)
    patched = patch_feed(verdicts, overrides)

    cost = (
        total["in"] / 1_000_000 * PRICE_IN_PER_MTOK
        + total["out"] / 1_000_000 * PRICE_OUT_PER_MTOK
        + total["searches"] / 1_000 * PRICE_SEARCH_PER_1K
    )
    print(
        f"\n자동 조사 {len(targets)}편 → 있음 {tally['yes']} · 없음 {tally['no']} "
        f"· 미확인 {tally['unknown']} · 검증 탈락 {demoted}"
    )
    print(
        f"  토큰 입력 {total['in']:,} · 출력 {total['out']:,} · 웹 검색 {total['searches']}회"
        f" → 대략 ${cost:.2f}"
    )
    if patched:
        print(f"  오늘 피드에 제자리 반영 {patched}편 (cookies.json · data.js)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
