#!/usr/bin/env python3
"""갱신 회차 실행 요약 — GitHub Actions 의 '실행 요약' 패널에 붙일 마크다운을 만든다.

로그를 끝까지 스크롤해야만 오늘 무슨 일이 있었는지 알 수 있다면, 사실상 아무도
안 본다. 그래서 회차마다 '작품 몇 편, TOP 10 중 몇 편, 미확인 어떤 작품,
자동 조사 결과, 무엇이 실패했는지'를 한 화면에 모은다.

읽는 것:
  - ios/data/cookies.json (또는 data.js) — 오늘 발행된 피드
  - '데이터 갱신' 단계 로그 (tee 로 남긴 파일)
  - '쿠키 자동 조사' 단계 로그
  - data/verdicts-auto.json

내는 것:
  - 마크다운 → $GITHUB_STEP_SUMMARY (없으면 표준출력)
  - `::warning::` → 표준출력 (GitHub 이 주석으로 올린다)

사용법:
  python3 tools/summary.py --log /tmp/refresh.log --research-log /tmp/research.log
"""

import argparse
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# TOP 10 중 이보다 적게 실리면 박스오피스 화면이 듬성해진다 — 예전에 3편까지
# 떨어진 적이 있고, 그때 로그만 봐서는 알 수 없었다.
TOP10_MIN = 8


def _strip_prefix(line):
    """로그 한 줄에서 앞머리를 떼어낸다.

    두 가지 모양을 다 받는다:
      - 단계 출력을 그대로 tee 한 줄:      "  쿠키 있음 5 · 없음 9 · 미확인 9"
      - `gh run view --log` 가 내는 줄:    "refresh\t데이터 갱신\t2026-…Z   쿠키 있음 …"
    사람이 손으로 받은 로그로도 이 스크립트를 돌려 볼 수 있어야 하기 때문이다.
    """
    line = line.rstrip("\n").lstrip("﻿")
    parts = line.split("\t")
    if len(parts) >= 3:
        line = parts[-1]
    line = line.lstrip("﻿")
    return re.sub(r"^\d{4}-\d{2}-\d{2}T[\d:.]+Z ?", "", line)


def read_log(path):
    if not path:
        return []
    p = pathlib.Path(path)
    if not p.exists():
        return []
    return [_strip_prefix(l) for l in p.read_text(encoding="utf-8", errors="ignore").splitlines()]


def find(lines, pattern):
    """정규식에 맞는 **마지막** 줄의 match. 회차가 여러 번 찍혀도 최신을 쓴다."""
    hit = None
    rx = re.compile(pattern)
    for l in lines:
        m = rx.search(l)
        if m:
            hit = m
    return hit


def load_feed():
    """피드를 읽는다. cookies.json 이 우선, 없으면 data.js 에서 긁어낸다."""
    p = ROOT / "ios" / "data" / "cookies.json"
    if p.exists():
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            return d.get("updated"), d.get("boxofficeDate"), d.get("movies", [])
        except (json.JSONDecodeError, OSError):
            pass
    js = ROOT / "data.js"
    if not js.exists():
        return None, None, []
    text = js.read_text(encoding="utf-8")
    updated = (re.search(r"const DATA_UPDATED = '([^']*)'", text) or [None, None])[1]
    bo = (re.search(r"const BOXOFFICE_DATE = (\S+);", text) or [None, "null"])[1]
    try:
        bo = json.loads(bo)
    except json.JSONDecodeError:
        bo = None
    m = re.search(r"(?s)const MOVIES = (\[.*?\n\]);", text)
    movies = json.loads(m.group(1)) if m else []
    return updated, bo, movies


def build(args):
    updated, bo_date, movies = load_feed()
    log = read_log(args.log)
    rlog = read_log(args.research_log)

    tally = {"yes": 0, "no": 0, "unknown": 0}
    for m in movies:
        tally[m.get("status", "unknown")] = tally.get(m.get("status", "unknown"), 0) + 1
    unknown = [m for m in movies if m.get("status") == "unknown"]

    out = ["## 쿠키이써 데이터 갱신", ""]
    out.append(f"- 조회일 **{updated or '?'}** · 박스오피스 기준일 **{bo_date or '없음'}** · 작품 **{len(movies)}편**")

    cov = find(log, r"KOBIS TOP (\d+) 중 (\d+)편")
    top_n = cov_n = None
    if cov:
        top_n, cov_n = int(cov.group(1)), int(cov.group(2))
        out.append(f"- **KOBIS TOP {top_n} 중 {cov_n}편** 수록")
    else:
        ranked = sum(1 for m in movies if m.get("boRank"))
        out.append(f"- 박스오피스 집계 {ranked}편 (로그에서 커버리지 줄을 찾지 못함)")

    out.append(f"- 쿠키 있음 **{tally['yes']}** · 없음 **{tally['no']}** · 미확인 **{tally['unknown']}**")
    out.append("")

    if unknown:
        out.append("### 미확인 작품")
        out.append("")
        for m in unknown:
            rank = f"BO {m['boRank']}위 · " if m.get("boRank") else ""
            out.append(f"- {m.get('title')} (#{m.get('tmdbId')}) — {rank}개봉 {m.get('releaseDate') or '?'}")
        out.append("")

    # --- 자동 조사 -----------------------------------------------------------
    out.append("### 쿠키 자동 조사")
    out.append("")
    res = find(rlog, r"자동 조사 (\d+)편 → 있음 (\d+) · 없음 (\d+) · 미확인 (\d+) · 검증 탈락 (\d+)")
    demoted = 0
    if res:
        n, y, no, unk, demoted = (int(res.group(i)) for i in range(1, 6))
        out.append(f"- {n}편 조사 → 있음 **{y}** · 없음 **{no}** · 미확인 **{unk}** · 검증 탈락 **{demoted}**")
        cost = find(rlog, r"(토큰 입력 .*→ 대략 \$[\d.]+)")
        if cost:
            out.append(f"- {cost.group(1)}")
        for l in rlog:
            m = re.search(r"^\s*\[(yes|no)\] (.+)$", l)
            if m:
                out.append(f"  - `{m.group(1)}` {m.group(2)}")
    elif find(rlog, r"자동 조사 건너뜀 — 인증 없음"):
        out.append("- 건너뜀 — Anthropic 인증이 없습니다 (번역도 함께 빠집니다)")
    elif find(rlog, r"자동 조사 대상 없음"):
        out.append("- 대상 없음 — 미확인이 없거나 모두 최근에 조사했습니다")
    elif not rlog:
        # 조사는 아침 첫 예약(과 수동 실행)에서만 돈다 — 나머지 회차는 이게 정상이다.
        out.append("- 이 회차에서는 돌지 않았습니다 (아침 첫 예약·수동 실행에서만)")
    else:
        out.append("- 실행 기록을 찾지 못했습니다")

    verdicts = {}
    vp = ROOT / "data" / "verdicts-auto.json"
    if vp.exists():
        try:
            verdicts = json.loads(vp.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            verdicts = {}
    if verdicts:
        settled = sum(1 for v in verdicts.values() if v.get("status") in ("yes", "no"))
        out.append(f"- 누적 자동 판정 {settled}편 / 기록 {len(verdicts)}편 (`data/verdicts-auto.json`)")
    out.append("")

    # --- 소스 상태 -----------------------------------------------------------
    out.append("### 소스 상태")
    out.append("")
    ac = find(log, r"aftercredits 조회 실패 (\d+)편")
    ac_fail = int(ac.group(1)) if ac else 0
    out.append(f"- aftercredits 조회 실패: **{ac_fail}편**" if ac_fail else "- aftercredits: 정상")

    ko = find(log, r"나무위키 색인에서 채움 (\d+)편")
    out.append(f"- 나무위키 색인에서 채움: {ko.group(1)}편" if ko else "- 나무위키 색인: 기록 없음")

    auto_fill = find(log, r"자동 조사에서 채움 (\d+)편")
    if auto_fill:
        out.append(f"- 자동 조사 판정에서 채움: {auto_fill.group(1)}편")

    # 나무위키 라이브 조회는 러너 IP 가 Cloudflare 에 막혀 **매일** 실패한다.
    # 경고로 올리면 매일 울려 아무도 안 보게 되므로 요약에만 적는다.
    out.append("- 나무위키 라이브 조회: 러너 IP 차단(Cloudflare) — 색인으로 대체 (정상 동작)")
    out.append("")
    out.append("> 자동 판정이 틀렸다면 `data.overrides.json` 에서 고쳐 주세요. override 가 항상 이깁니다.")

    warnings = []
    if cov_n is not None and cov_n < TOP10_MIN:
        warnings.append(f"KOBIS TOP {top_n} 중 {cov_n}편만 실렸습니다 (기준 {TOP10_MIN}편)")
    if ac_fail:
        warnings.append(f"aftercredits 조회가 {ac_fail}편에서 실패했습니다 — '없음'과 구분되지 않습니다")
    if demoted:
        warnings.append(f"자동 조사 검증 탈락 {demoted}편 — 모델이 확인되지 않는 근거를 냈습니다")

    return "\n".join(out) + "\n", warnings


def main(argv=None):
    ap = argparse.ArgumentParser(description="갱신 회차 실행 요약 마크다운")
    ap.add_argument("--log", default=None, help="'데이터 갱신' 단계 로그 파일")
    ap.add_argument("--research-log", default=None, help="'쿠키 자동 조사' 단계 로그 파일")
    ap.add_argument("--out", default=None, help="마크다운을 쓸 파일 (기본: $GITHUB_STEP_SUMMARY, 없으면 표준출력)")
    args = ap.parse_args(argv)

    md, warnings = build(args)
    out = args.out or os.environ.get("GITHUB_STEP_SUMMARY")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(md)
    else:
        sys.stdout.write(md)
    for w in warnings:
        print(f"::warning::{w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
