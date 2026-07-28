#!/usr/bin/env bash

set -euo pipefail

# 이 스크립트가 어느 위치에서 실행되더라도 경로가 동일하게 동작하도록
# 스크립트 디렉터리와 rag_test 프로젝트 루트를 따로 계산합니다.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# 개발 에이전트가 매번 읽어야 하는 공통 지침입니다.
INSTRUCTIONS_PATH="agent/instructions.md"

# 사용자가 이번 변경사항을 작성하는 고정 파일입니다.
CHANGE_PATH="agent/project_spec/change_request.md"

# 성공한 변경 요청을 보관하는 디렉터리입니다.
HISTORY_DIR="agent/project_spec/history"

# Codex 실행 로그를 보관하는 디렉터리입니다.
LOG_DIR="agent/logs"

# 필요한 명령어가 설치되어 있는지 확인합니다.
if ! command -v git >/dev/null 2>&1; then
  echo "git 명령어를 찾을 수 없습니다."
  exit 1
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "codex 명령어를 찾을 수 없습니다."
  exit 1
fi

# Codex에 전달할 입력 문서가 존재하는지 확인합니다.
for required_file in \
  "$INSTRUCTIONS_PATH" \
  "$CHANGE_PATH" \
  "agent/project_spec/current/requirements.md" \
  "agent/project_spec/current/architecture.md" \
  "agent/project_spec/current/api_contract.md"
do
  if [ ! -f "$required_file" ]; then
    echo "필수 입력 문서를 찾을 수 없습니다:"
    echo "$required_file"
    exit 1
  fi
done

# 공백을 제외한 실제 내용이 있는지 확인합니다.
if ! grep -q '[^[:space:]]' "$CHANGE_PATH"; then
  echo "변경 요청 파일이 비어 있습니다."
  echo "$CHANGE_PATH 파일에 이번 변경사항을 작성해주세요."
  exit 1
fi

mkdir -p "$HISTORY_DIR"

# change_request.md는 사용자가 방금 작성한 파일이므로
# 커밋되지 않은 상태여도 허용합니다.
#
# 그 외 파일에 기존 변경사항이 있다면
# 이번 에이전트 작업과 섞이지 않도록 중단합니다.
OTHER_CHANGES="$(
  git status --porcelain |
    awk -v allowed="$CHANGE_PATH" '$2 != allowed { print }'
)"

if [ -n "$OTHER_CHANGES" ]; then
  echo "change_request.md 외에 커밋되지 않은 변경사항이 있습니다."
  echo "기존 변경사항을 먼저 커밋하거나 stash한 후 다시 실행해주세요."
  echo
  printf '%s\n' "$OTHER_CHANGES"
  exit 1
fi

# Codex가 작업 도중 change_request.md를 수정하더라도
# 사용자가 처음 작성한 요청 내용은 보존해야 합니다.
#
# 따라서 실행 전에 임시 복사본을 만듭니다.
REQUEST_SNAPSHOT="$(
  mktemp "${TMPDIR:-/tmp}/rag-test-change.XXXXXX"
)"

# 스크립트가 끝날 때 임시 파일을 삭제합니다.
trap 'rm -f "$REQUEST_SNAPSHOT"' EXIT

cp "$CHANGE_PATH" "$REQUEST_SNAPSHOT"

# 스크립트가 실패하거나 중간에 종료되면
# change_request.md를 실행 전 내용으로 복원합니다.
RESTORE_CHANGE_REQUEST=1

cleanup() {
  if [ "$RESTORE_CHANGE_REQUEST" -eq 1 ] &&
     [ -f "$REQUEST_SNAPSHOT" ]; then
    cp "$REQUEST_SNAPSHOT" "$CHANGE_PATH"
  fi

  rm -f "$REQUEST_SNAPSHOT"
}

trap cleanup EXIT

# change_request.md 안에 아래와 같은 줄이 있으면:
#
# slug: common-logger
#
# history 파일명 뒤에 common-logger를 사용합니다.
SLUG="$(
  sed -nE \
    's/^[[:space:]]*slug:[[:space:]]*([A-Za-z0-9._-]+)[[:space:]]*$/\1/p' \
    "$REQUEST_SNAPSHOT" |
    head -n 1
)"

# slug가 없으면 기본 이름을 사용합니다.
SLUG="${SLUG:-change-request}"

# 파일명으로 안전하게 사용할 수 있도록 정리합니다.
SLUG="$(
  printf '%s' "$SLUG" |
    tr '[:upper:]' '[:lower:]' |
    sed -E 's/[^a-z0-9._-]+/-/g; s/^-+//; s/-+$//'
)"

SLUG="${SLUG:-change-request}"

# history 파일 중 가장 큰 일련번호를 찾습니다.
#
# 예:
# 20260728-001-common-logger.md
# 20260729-002-document-delete.md
#
# 위 파일들이 있다면 다음 번호는 003이 됩니다.
# 아래 명령어는 Mac 환경에 맞춤.
LAST_SEQUENCE="$(
  for history_file in "$HISTORY_DIR"/????????-???-*.md; do
    [ -f "$history_file" ] || continue
    basename "$history_file"
  done |
    sed -E 's/^[0-9]{8}-([0-9]{3})-.*\.md$/\1/' |
    sort -n |
    tail -n 1
)"

LAST_SEQUENCE="${LAST_SEQUENCE:-0}"

NEXT_SEQUENCE="$(
  printf '%03d' "$((10#$LAST_SEQUENCE + 1))"
)"

RUN_DATE="$(date '+%Y%m%d')"
RUN_TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"

ARCHIVE_PATH="$HISTORY_DIR/${RUN_DATE}-${NEXT_SEQUENCE}-${SLUG}.md"

# 로그 디렉터리가 없으면 생성합니다.
mkdir -p "$LOG_DIR"

# 실패한 실행도 덮어쓰지 않도록 시각을 파일명에 포함합니다.
LOG_PATH="$LOG_DIR/${RUN_TIMESTAMP}-${NEXT_SEQUENCE}-${SLUG}.log"

echo "변경 요청 파일:"
echo "$CHANGE_PATH"
echo
echo "작업 성공 후 보관 위치:"
echo "$ARCHIVE_PATH"
echo
echo "Codex 실행 로그 위치:"
echo "$LOG_PATH"
echo 
echo "Codex 개발 에이전트를 실행합니다."
echo

# 아래 중괄호 안에서 Codex에 전달할 전체 프롬프트를 만듭니다.
{
  echo "# 개발 에이전트 공통 지침"
  cat "$INSTRUCTIONS_PATH"

  echo
  echo "# 현재 요구사항"
  cat agent/project_spec/current/requirements.md

  echo
  echo "# 현재 아키텍처"
  cat agent/project_spec/current/architecture.md

  echo
  echo "# 현재 API 계약"
  cat agent/project_spec/current/api_contract.md

  echo
  echo "# 이번 변경 요청"
  cat "$REQUEST_SNAPSHOT"

  cat <<'PROMPT'

# 실행 지시

표준 입력으로 전달된 프로젝트 명세와 변경 요청을 읽어라.

현재 저장소를 먼저 조사하고,
이번 변경 요청과 관련된 부분만 수정하라.

프로젝트를 처음부터 다시 만들지 마라.
관련 없는 리팩터링을 하지 마라.
기존 공개 API와 기존 테스트는
명시적인 변경 요구가 없는 한 유지하라.

다음 순서로 작업하라.

1. 현재 코드와 테스트를 조사한다.
2. 변경 요구사항의 영향 범위를 판단한다.
3. 필요한 코드만 최소 범위로 수정한다.
4. 필요한 테스트를 추가하거나 수정한다.
5. 관련 테스트와 전체 테스트를 실행한다.
6. 테스트가 성공한 경우에만 현재 요구사항,
   API 계약, 아키텍처 문서를 실제 구현에 맞게 갱신한다.
7. 변경된 파일, 테스트 결과,
   설계 문서 변경 내용을 최종 보고한다.

다음 사항을 반드시 지켜라.

- 기존 테스트를 삭제하거나 무력화하지 마라.
- 테스트가 실패한 상태에서는 구현 완료라고 판단하지 마라.
- agent/project_spec/change_request.md를 수정하지 마라.
- agent/project_spec/history 디렉터리를 수정하지 마라.
- agent/logs 디렉터리를 수정하지 마라.
PROMPT

# 위에서 조립한 전체 내용을 Codex의 표준 입력으로 전달합니다.
} | codex exec \
  --sandbox workspace-write \
  - 2>&1 | tee "$LOG_PATH"

echo
echo "Codex 작업 후 전체 회귀 테스트를 다시 실행합니다."
echo

# Codex가 테스트를 실행했다고 하더라도
# 스크립트가 다시 한 번 직접 전체 테스트를 검증합니다.
if ! uv run python -m pytest -q; then
  echo
  echo "전체 테스트가 실패했습니다."
  echo
  echo "변경 요청은 history로 이동하지 않았습니다."
  echo "change_request.md도 그대로 유지했습니다."
  echo
  echo "다음 명령으로 수정 내용을 확인해주세요:"
  echo "git status"
  echo "git diff"
  exit 1
fi

# Codex 실행과 전체 테스트가 모두 성공했을 때만
# 변경 요청을 history에 보관합니다.
cp "$REQUEST_SNAPSHOT" "$ARCHIVE_PATH"

# 다음 요구사항을 작성할 수 있도록
# 현재 change_request.md를 빈 파일로 만듭니다.
: > "$CHANGE_PATH"

# 정상적으로 작업을 완료했으므로
# 종료 시 원래 요청 내용으로 복원하지 않습니다.
RESTORE_CHANGE_REQUEST=0

echo
echo "작업과 전체 테스트가 성공했습니다."
echo
echo "변경 요청을 다음 위치에 보관했습니다:"
echo "$ARCHIVE_PATH"
echo
echo "다음 명령으로 최종 변경사항을 확인하세요:"
echo "git status"
echo "git diff"