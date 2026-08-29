"""쿠키 설명 한국어 번역 (선택 기능).

aftercredits.com 의 쿠키 설명은 영어다. 이 앱은 한국어라서 그대로 두면 어색하므로
`--translate` 를 주면 Claude API 로 번역한다. 없으면 영어 원문을 그대로 쓴다 —
번역 실패가 파이프라인을 멈추게 하지 않는다.

필요한 것:
  pip install anthropic
  export ANTHROPIC_API_KEY=...        # 또는 `ant auth login` 으로 프로필 설정

번역 결과는 tools/.translation-cache.json 에 원문 해시로 캐시되므로, 같은 문장을
두 번 번역하지 않는다 (매일 갱신해도 새 작품 몫만 비용이 든다).
"""

import hashlib
import json
import pathlib

CACHE_PATH = pathlib.Path(__file__).resolve().parent / ".translation-cache.json"

MODEL = "claude-opus-5"

SYSTEM = """너는 영화 '쿠키 영상'(post-credits scene) 설명을 한국어로 옮기는 번역가다.

규칙:
- 영화 팬이 읽는 짧은 안내문이다. 자연스러운 한국어 구어체 종결어미('~합니다', '~됩니다')를 쓴다.
- 내용을 요약하거나 덧붙이지 말고 있는 그대로 옮긴다. 스포일러를 흐리지 않는다.
- 등장인물·작품명 등 고유명사는 국내 통용 표기가 있으면 그것을 쓰고, 없으면 원어를 남긴다.
- 입력 순서와 같은 순서로, 같은 개수의 번역문을 돌려준다."""

SCHEMA = {
    "type": "object",
    "properties": {
        "translations": {
            "type": "array",
            "items": {"type": "string"},
            "description": "입력과 같은 순서, 같은 개수의 한국어 번역문",
        }
    },
    "required": ["translations"],
    "additionalProperties": False,
}


def _key(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def _load_cache():
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def _save_cache(cache):
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")


def translate(texts):
    """영어 문장 리스트를 한국어로. 실패하면 원문을 그대로 돌려준다.

    반환값은 항상 입력과 같은 길이다.
    """
    texts = list(texts)
    if not texts:
        return []

    cache = _load_cache()
    todo = [t for t in dict.fromkeys(texts) if t.strip() and _key(t) not in cache]

    if todo:
        fresh = _call_api(todo)
        if fresh is None:
            return texts  # 번역 불가 — 영어 원문 유지
        cache.update({_key(src): ko for src, ko in zip(todo, fresh)})
        _save_cache(cache)

    return [cache.get(_key(t), t) for t in texts]


def _call_api(texts):
    """Claude 로 일괄 번역. SDK/자격증명/응답 문제는 전부 None 으로 흡수한다."""
    try:
        import anthropic
    except ImportError:
        print("  [번역 건너뜀] pip install anthropic 이 필요합니다 — 영어 원문을 유지합니다.")
        return None

    numbered = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(texts))
    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": f"다음 {len(texts)}개 문장을 번역해라.\n\n{numbered}",
                }
            ],
            output_config={
                "effort": "low",
                "format": {"type": "json_schema", "schema": SCHEMA},
            },
        )
    except Exception as exc:  # 자격증명 없음, 요금 한도, 네트워크 등
        print(f"  [번역 건너뜀] {type(exc).__name__}: {exc} — 영어 원문을 유지합니다.")
        return None

    try:
        result = json.loads(response.content[0].text)["translations"]
    except (KeyError, IndexError, ValueError, AttributeError):
        print("  [번역 건너뜀] 응답을 해석하지 못했습니다 — 영어 원문을 유지합니다.")
        return None

    if len(result) != len(texts):
        print(
            f"  [번역 건너뜀] 개수가 맞지 않습니다 ({len(result)} != {len(texts)}) — 영어 원문을 유지합니다."
        )
        return None
    return result


def _needs_translation(text):
    """이미 한국어인 설명(나무위키 출처 등)은 건드리지 않는다."""
    hangul = sum("가" <= ch <= "힣" for ch in text)
    return hangul < len(text) * 0.2


def translate_movies(movies):
    """movies 안의 영어 쿠키 설명을 제자리에서 번역한다."""
    targets = [
        (m, c) for m in movies for c in m["cookies"] if c.get("desc") and _needs_translation(c["desc"])
    ]
    if not targets:
        return movies
    print(f"쿠키 설명 번역 중… ({len(targets)}개)")
    translated = translate([c["desc"] for _, c in targets])
    for (_, cookie), ko in zip(targets, translated):
        cookie["desc"] = ko
    return movies
