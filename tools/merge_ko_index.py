#!/usr/bin/env python3
"""나무위키 색인(data/ko-index.json) 두 벌을 합친다 — 발행 전 병합 로직.

tools/publish_index.sh 가 부른다. 셸에서 떼어 둔 이유는 **네트워크 없이 시험할 수
있어야 하기 때문**이다. 발행 사고는 조용히 나고(어제 것이 오늘 것을 덮어씀) 며칠
뒤에야 드러나므로, 이 로직만은 단위로 확인할 수 있어야 한다.

규칙은 하나다: **색인은 더해지기만 한다.**
  entries  합집합. 양쪽에 있으면 로컬이 이긴다 (맥이 방금 문서를 본 쪽).
  checked  합집합. 한쪽에만 있어도 남긴다.
  syncedAt 둘 중 큰 값.

원격 항목이 사라지는 경로가 없어야 한다. 러너도 (막히지 않았다면) 색인에 쓸 수
있고, 무엇보다 예전에 로컬 사본이 원격 피드를 덮어써 매일 데이터를 퇴행시킨 적이
있다 — 색인에서는 그 사고가 **구조적으로 불가능**해야 한다.

사용법:
  python3 tools/merge_ko_index.py --local data/ko-index.json \
      --remote remote.json --out merged.json
  → stdout 에 CHANGED 또는 SAME 한 줄 (셸이 읽는다), 통계는 stderr.
"""

import argparse
import json
import sys


def _norm_checked(values):
    """checked 는 TMDB id 목록이다. 숫자로 맞춰 두면 정렬도 비교도 흔들리지 않는다."""
    out = set()
    for v in values or []:
        try:
            out.add(int(v))
        except (TypeError, ValueError):
            out.add(v)
    return out


def _sort_key(v):
    return (1, str(v)) if isinstance(v, str) else (0, v)


def empty_index():
    return {"syncedAt": None, "entries": {}, "checked": []}


def merge(local, remote):
    """로컬·원격 색인을 합친 새 색인을 돌려준다 (둘 다 건드리지 않는다)."""
    local = local or empty_index()
    remote = remote or empty_index()

    entries = dict(remote.get("entries") or {})
    entries.update(local.get("entries") or {})   # 겹치면 로컬이 이긴다

    checked = _norm_checked(remote.get("checked")) | _norm_checked(local.get("checked"))

    synced = [s for s in (local.get("syncedAt"), remote.get("syncedAt")) if s]
    return {
        "syncedAt": max(synced) if synced else None,
        "entries": entries,
        "checked": sorted(checked, key=_sort_key),
    }


def is_same(merged, remote):
    """올릴 것이 있는가. syncedAt 은 비교에서 뺀다.

    시각만 달라진 파일을 매일 올리면 내용 없는 커밋이 쌓인다 — 정작 무엇이
    언제 늘었는지 이력에서 안 보이게 된다. 아는 것(entries)이나 본 것(checked)이
    늘었을 때만 올린다.
    """
    remote = remote or empty_index()
    return (
        merged["entries"] == (remote.get("entries") or {})
        and merged["checked"] == sorted(_norm_checked(remote.get("checked")), key=_sort_key)
    )


def _load(path):
    if not path:
        return empty_index()
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read().strip()
    except FileNotFoundError:
        return empty_index()
    if not text:
        return empty_index()
    data = json.loads(text)
    data.setdefault("entries", {})
    data.setdefault("checked", [])
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", required=True)
    ap.add_argument("--remote")          # 없거나 빈 파일이면 첫 발행으로 본다
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    local, remote = _load(args.local), _load(args.remote)
    merged = merge(local, remote)
    same = is_same(merged, remote)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False)

    le, re_ = len(local["entries"]), len(remote["entries"])
    print(
        f"  병합 — 로컬 {le}편 · 원격 {re_}편 → {len(merged['entries'])}편"
        f" (확인 누적 {len(merged['checked'])}편)\n"
        f"  원격에만 있던 항목 {len(set(remote['entries']) - set(local['entries']))}편 유지"
        f" · 로컬이 덮어쓴 항목 {len(set(remote['entries']) & set(local['entries']))}편",
        file=sys.stderr,
    )
    print("SAME" if same else "CHANGED")


if __name__ == "__main__":
    main()
