#!/bin/zsh
# data/ko-index.json (나무위키 쿠키 색인) 하나만 데이터 저장소에 발행한다.
#
# **왜 이 스크립트가 있나.** 나무위키는 한국·일본 영화 쿠키 정보의 유일한 출처인데,
# GitHub Actions 러너 IP 는 Cloudflare 에 막혀 있다 (차단은 그쪽 정책이고 존중한다 —
# 우회하지 않는다). 그래서 '발견'과 '발행'을 나눈다: 나무위키가 닿는 이 맥이 색인을
# 채워 올리고, KOBIS 키가 있는 Actions 가 그 색인을 읽어 피드를 만든다. 쿠키 유무는
# 한 번 확정되면 변하지 않는 사실이라, 이렇게 시차를 두어도 틀리지 않는다.
#
# **올리는 파일은 색인 하나뿐이다.** cookies.json·data.js 는 건드리지 않는다.
# 예전에 이 맥이 피드를 통째로 올려 매일 8/30 집계로 퇴행시킨 사고가 있었다
# (KOBIS 키가 여기 없어 로컬 피드가 늘 낡는다). 색인은 '더해지기만 하는 지식'이라
# 그 사고가 구조적으로 일어날 수 없는 유일한 파일이다.
#
# 사용법:
#   zsh tools/publish_index.sh                 # sync 후 발행 (budget 60)
#   zsh tools/publish_index.sh --budget 120
#   zsh tools/publish_index.sh --dry-run       # 병합 결과만 보고 끝 (올리지 않음)
#   zsh tools/publish_index.sh --skip-sync     # 이미 돈 색인을 그대로 올린다
#
# 선행 조건: gh CLI 로그인, TMDB_READ_TOKEN (sync 단계에 필요).
# launchd 로 매일 도는 설정은 tools/launchd/com.cookiecheck.publish-index.plist.
#
# **저장소 루트는 위치 독립적이다.** launchd 에이전트는 macOS TCC 때문에
# 이 프로젝트가 있던 원래 폴더를 읽을 수 없다 (ls 는 되지만 cat 은 안 된다 —
# 확인됨). 그래서 실제 실행은 ~/Library/Application Support/cookiecheck/repo
# 의 자체 clone 에서 돈다 (tools/launchd/install.sh 가 만든다). COOKIECHECK_ROOT
# 환경변수가 있으면 그 경로를, 없으면 스크립트 위치 기준(원래 프로젝트 사본에서
# 손으로 돌릴 때)을 저장소 루트로 쓴다.

set -euo pipefail

if [[ -n "${COOKIECHECK_ROOT:-}" ]]; then
  cd "$COOKIECHECK_ROOT"
else
  cd "$(dirname "$0")/.."
fi
ROOT="$PWD"

REPO="realkose1/cookiecheck-data"
DEST="data/ko-index.json"
LOCAL="data/ko-index.json"
BUDGET=60
DRY=0
SKIP_SYNC=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --budget)    BUDGET="$2"; shift 2 ;;
    --dry-run)   DRY=1; shift ;;
    --skip-sync) SKIP_SYNC=1; shift ;;
    *) echo "모르는 인자: $1"; exit 2 ;;
  esac
done

echo "=== 쿠키 색인 발행 $(date '+%F %T') (root: $ROOT) ==="

# 0) 자체 clone 이면 러너가 채운 최신 코드·색인을 먼저 받는다. 오프라인일
#    수 있으니 실패해도 계속 진행한다 (로그에 남긴다).
IS_GIT_REPO=0
if git rev-parse --is-inside-work-tree &>/dev/null; then
  IS_GIT_REPO=1
  echo "▸ git pull --rebase origin main…"
  if git pull --rebase --quiet origin main; then
    echo "  최신입니다."
  else
    echo "  pull 실패 — 오프라인이거나 충돌일 수 있습니다. 가진 것으로 계속합니다."
  fi
fi

# TMDB 토큰: 원래 프로젝트 사본이면 Secrets.xcconfig 에서, 자체 clone 이면
# 옆의 .env 에서 읽는다 (launchd 는 셸 환경을 물려받지 않는다).
if [[ -z "${TMDB_READ_TOKEN:-}" ]]; then
  if [[ -f ios/Config/Secrets.xcconfig ]]; then
    TMDB_READ_TOKEN=$(grep '^TMDB_READ_TOKEN' ios/Config/Secrets.xcconfig | sed 's/.*= *//')
    export TMDB_READ_TOKEN
  elif [[ -f "$ROOT/../.env" ]]; then
    source "$ROOT/../.env"
  fi
fi

if [[ -z "${TMDB_READ_TOKEN:-}" ]]; then
  echo "TMDB_READ_TOKEN 을 찾을 수 없습니다 — ios/Config/Secrets.xcconfig 도," \
       "$ROOT/../.env 도 없습니다. tools/launchd/install.sh 를 먼저 실행하세요." >&2
  exit 1
fi

# 1) 색인 갱신. 나무위키가 막혀 있으면 sync_namu.py 가 스스로 건너뛴다.
if [[ "$SKIP_SYNC" == "0" ]]; then
  python3 tools/sync_namu.py --budget "$BUDGET"
fi

[[ -f "$LOCAL" ]] || { echo "색인 파일이 없습니다: $LOCAL"; exit 1; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# 2) 원격을 받아 합치고, 늘어난 게 있을 때만 올린다.
#    Actions 가 같은 파일을 커밋하면 sha 가 어긋나 409 가 온다 — 그때는 원격을
#    다시 받아 병합하고 한 번만 재시도한다 (러너 커밋을 절대 잃지 않기 위해서다).
publish() {
  local attempt="$1"

  gh api "repos/$REPO/contents/$DEST" --jq .content 2>/dev/null \
    | base64 -d > "$TMP/remote.json" 2>/dev/null || : > "$TMP/remote.json"
  local sha
  sha=$(gh api "repos/$REPO/contents/$DEST" --jq .sha 2>/dev/null || true)

  local verdict
  verdict=$(python3 tools/merge_ko_index.py \
              --local "$LOCAL" --remote "$TMP/remote.json" --out "$TMP/merged.json")

  if [[ "$verdict" == "SAME" ]]; then
    echo "  올릴 것 없음 — 원격 색인과 같습니다."
    return 0
  fi

  if [[ "$DRY" == "1" ]]; then
    echo "  [dry-run] 올릴 것 있음 — 여기서 멈춥니다. 병합 결과: $TMP/merged.json"
    cp "$TMP/merged.json" /tmp/ko-index-merged-preview.json
    echo "  [dry-run] 미리보기 사본: /tmp/ko-index-merged-preview.json"
    return 0
  fi

  local args=(-X PUT -f "message=ko-index: $(date +%F)"
              -f "content=$(base64 -i "$TMP/merged.json" | tr -d '\n')")
  [[ -n "$sha" ]] && args+=(-f "sha=$sha")

  local out
  if out=$(gh api "repos/$REPO/contents/$DEST" "${args[@]}" --jq .commit.sha 2>&1); then
    echo "  발행 완료 ($out) → https://raw.githubusercontent.com/$REPO/main/$DEST"
    # 원격이 알던 것을 로컬도 알게 해 둔다 — 다음 sync 가 러너가 이미 본 문서를
    # 다시 두드리지 않는다.
    cp "$TMP/merged.json" "$LOCAL"
    # 자체 clone 의 작업 트리는 매번 깨끗하게 되돌려 둔다 — 원격이 진실이고
    # 다음 실행이 어차피 git pull --rebase 로 다시 받으므로, 로컬 변경을
    # 남겨 두면 리베이스가 막힐 수 있다.
    if [[ "$IS_GIT_REPO" == "1" ]]; then
      git checkout -- "$LOCAL" 2>/dev/null || true
    fi
    return 0
  fi

  if [[ "$out" == *409* || "$out" == *"does not match"* ]] && [[ "$attempt" == "1" ]]; then
    echo "  충돌(409) — 그 사이 러너가 색인을 커밋했습니다. 다시 받아 병합합니다."
    sleep 3
    publish 2
    return $?
  fi

  echo "  발행 실패: $out"
  return 1
}

publish 1
