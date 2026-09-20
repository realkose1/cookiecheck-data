#!/bin/zsh
# launchd 에이전트(com.cookiecheck.publish-index)를 원래 프로젝트 폴더 밖,
# 자체 작업 사본에서 돌게 설치/재설치한다. 두 번 실행해도 안전하다(멱등).
#
# **왜 필요한가.** macOS TCC 는 launchd 에이전트가 그 폴더를 읽는 것을 막는다
# (ls 는 되고 cat 은 안 된다 — 실제 bootstrap 된 에이전트로 재현 완료).
# 그래서 실제 실행은 ~/Library/Application Support/cookiecheck/repo 의
# realkose1/cookiecheck-data clone 에서 돈다. 그 저장소에는 tools/*.py,
# data/ko-index.json, ios/data/cookies.json 이 전부 있어 sync_namu.py 가
# 필요한 건 다 있다. 없는 건 TMDB 토큰 하나뿐이라 옆에 .env 로 둔다.
#
# ~/Library/LaunchAgents 는 root 소유(회사 보안 SW)라 plist 교체에는 sudo 가
# 필요하다 — 이 스크립트를 터미널에서 직접 실행해야 한다 (launchd 로는 못 돈다).
#
# 사용법: zsh tools/launchd/install.sh

set -euo pipefail

APP_SUPPORT="$HOME/Library/Application Support/cookiecheck"
REPO_DIR="$APP_SUPPORT/repo"
ENV_FILE="$APP_SUPPORT/.env"
LABEL="com.cookiecheck.publish-index"
PLIST_NAME="$LABEL.plist"
STAGE_PLIST="$APP_SUPPORT/$PLIST_NAME"
DEST_PLIST="$HOME/Library/LaunchAgents/$PLIST_NAME"
LOG_FILE="$HOME/Library/Logs/cookiecheck-publish-index.log"
SECRETS_XCCONFIG="/Users/user/Desktop/cookiebox/ios/Config/Secrets.xcconfig"

echo "▸ 1/6 작업 사본 준비: $REPO_DIR"
mkdir -p "$APP_SUPPORT"
if [[ -d "$REPO_DIR/.git" ]]; then
  echo "  이미 있습니다 — pull --rebase 로 최신화합니다."
  git -C "$REPO_DIR" pull --rebase --quiet
else
  gh repo clone realkose1/cookiecheck-data "$REPO_DIR"
fi

echo "▸ 2/6 TMDB 토큰을 .env 로 옮기는 중 (값은 출력하지 않습니다)"
if [[ ! -f "$SECRETS_XCCONFIG" ]]; then
  echo "  Secrets.xcconfig 를 찾을 수 없습니다: $SECRETS_XCCONFIG" >&2
  exit 1
fi
TMDB_TOKEN_LINE=$(grep '^TMDB_READ_TOKEN' "$SECRETS_XCCONFIG" || true)
if [[ -z "$TMDB_TOKEN_LINE" ]]; then
  echo "  Secrets.xcconfig 에 TMDB_READ_TOKEN 줄이 없습니다." >&2
  exit 1
fi
TMDB_TOKEN_VALUE=$(echo "$TMDB_TOKEN_LINE" | sed 's/.*= *//')
{
  echo "export TMDB_READ_TOKEN=\"$TMDB_TOKEN_VALUE\""
} > "$ENV_FILE"
chmod 600 "$ENV_FILE"
echo "  기록했습니다: $ENV_FILE (chmod 600)"

echo "▸ 3/6 plist 생성: $STAGE_PLIST"
cat > "$STAGE_PLIST" <<PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<!--
  나무위키 쿠키 색인을 매일 한 번 채워 올린다 (tools/publish_index.sh).

  왜 이 맥에서 도는가: GitHub Actions 러너 IP 는 나무위키 Cloudflare 에 막혀 있어
  한국·일본 영화 쿠키를 영원히 못 채운다. 우회하지 않고, 나무위키가 정상적으로
  닿는 이 맥이 색인을 채워 올리면 러너는 그 색인을 읽어 피드를 만든다.

  왜 원래 프로젝트 폴더가 아니라 Application Support 인가: macOS TCC 가 launchd
  에이전트의 그 폴더 읽기를 막는다 (ls 는 되지만 cat 은 안 된다). 그래서 이
  에이전트는 ~/Library/Application Support/cookiecheck/repo 의 자체 clone 에서 돈다.

  09:30 인 이유: KOBIS 전날 집계가 아침에 나오고 Actions 는 그 뒤로 하루 일곱 번
  도는데, 첫 회차(08:17 KST)와 둘째 회차(09:43 KST) 사이의 한산한 틈이다.
  겹쳐도 안전하게는 만들어 뒀지만(충돌 시 재시도) 굳이 부딪힐 이유는 없다.

  StartCalendarInterval 을 쓴 이유: 잠들어 있어 놓친 회차를 깨어난 뒤 한 번 돌려
  준다. StartInterval 은 그 보장이 없다.

  설치/재설치 (사용자가 직접, sudo 필요):
    zsh tools/launchd/install.sh
-->
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>$REPO_DIR/tools/publish_index.sh</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$REPO_DIR</string>

    <!-- launchd 는 로그인 셸 환경을 물려받지 않는다. gh 가 PATH 에 없으면
         발행 단계가 통째로 조용히 실패한다. (which gh → /opt/homebrew/bin/gh)
         COOKIECHECK_ROOT 는 publish_index.sh 에게 원래 프로젝트 폴더가 아니라
         이 자체 clone 을 저장소 루트로 쓰라고 알려준다. -->
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>HOME</key>
        <string>$HOME</string>
        <key>LANG</key>
        <string>ko_KR.UTF-8</string>
        <key>COOKIECHECK_ROOT</key>
        <string>$REPO_DIR</string>
    </dict>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>30</integer>
    </dict>

    <!-- 로그인 직후 한 번 더 돌지 않게. 예약 시각에만 돈다. -->
    <key>RunAtLoad</key>
    <false/>

    <key>StandardOutPath</key>
    <string>$LOG_FILE</string>
    <key>StandardErrorPath</key>
    <string>$LOG_FILE</string>

    <!-- 나무위키 문서당 1초를 지키므로 budget 만큼 시간이 걸린다. 넉넉히. -->
    <key>ExitTimeOut</key>
    <integer>1800</integer>

    <!-- 사람이 쓰는 동안 앞자리를 뺏지 않는다. 급한 작업이 아니다. -->
    <key>ProcessType</key>
    <string>Background</string>
    <key>LowPriorityIO</key>
    <true/>
    <key>Nice</key>
    <integer>5</integer>
</dict>
</plist>
PLIST_EOF

plutil -lint "$STAGE_PLIST"

echo "▸ 4/6 기존 에이전트 내리는 중"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true

echo "▸ 5/6 plist 를 LaunchAgents 로 옮기는 중 (sudo 필요 — 회사 보안 SW 가 폴더를 root 소유로 둡니다)"
sudo cp "$STAGE_PLIST" "$DEST_PLIST"
launchctl bootstrap "gui/$(id -u)" "$DEST_PLIST"
launchctl kickstart -p "gui/$(id -u)/$LABEL"

echo "▸ 6/6 8초 대기 후 상태 확인"
sleep 8
echo "--- 로그 마지막 15줄 ($LOG_FILE) ---"
tail -n 15 "$LOG_FILE" 2>/dev/null || echo "  (로그 파일이 아직 없습니다)"
echo "--- launchctl print: last exit code ---"
launchctl print "gui/$(id -u)/$LABEL" 2>/dev/null | grep -i "last exit code" || echo "  (아직 실행 기록이 없습니다)"

echo "✓ 설치 완료"
