# 1. ouroboros 설치

```bash
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 
source $HOME/.local/bin/env
uv --version

## >> 결과
((.venv) ) a454676@454676ui-MacBookPro rag_test % curl -LsSf https://astral.sh/uv/install.sh | sh
downloading uv 0.11.31 aarch64-apple-darwin
installing to /Users/a454676/.local/bin
  uv
  uvx
everything's installed!

To add $HOME/.local/bin to your PATH, either restart your shell or run:

    source $HOME/.local/bin/env (sh, bash, zsh)
    source $HOME/.local/bin/env.fish (fish)
((.venv) ) a454676@454676ui-MacBookPro rag_test % source $HOME/.local/bin/env
((.venv) ) a454676@454676ui-MacBookPro rag_test % uv --version
uv 0.11.31 (b7fdec626 2026-07-21 aarch64-apple-darwin)

```
```bash
uv python install 3.12
uv tool install --python 3.12 "ouroboros-ai[mcp]"


# 설치 확인
ouroboros --version

```
rag_test/.venv
→ 내가 만드는 RAG 프로그램용

uv 내부의 Ouroboros 환경
→ Ouroboros 실행용


# 2. codex cli 설치 여부 확인

```bash
brew install node

npm install -g @openai/codex

codex --version

```

# 3. ouroboros 초기 설정
```bash
ouroboros setup
>> 결과
# 난 codex, copilot 이 떴다. 1 (코덱스) 를 입력해준다.

>> 결과

Setup complete!

Next steps:
  ouroboros init start "your idea here"
  ouroboros run workflow seed.yaml

# 위와 같이 떴다.
인터뷰 하는 방법은 ooo interview 라고 들었지만, 일단 안내에 따라 init 부터 수행해보자.
```

# 실행 로그 분석
```bash
AC:  Acceptance Criteria, 완료 조건 (인수 기준)
기능이 완성됐다고 인정하려면 무엇이 되어 있어야 하는가? 의 기준을 적어둔 것.

# 문제점 찾기 - 1
## 로그를 보면 test worktress 경로가 나와있다.
## 해당 워크트리 로 이동 후 
## 실제로 파일을 실행시켜 문제점이 있는지 확인한다.
((.venv) ) a454676@454676ui-MacBookPro rag_test %       ouroboros run workflow --runtime codex --project-dir . --debug ouroboros/seeds/seed_f101692bd03c.yaml
╭──────────────────────────────────────────────────────── Info ────────────────────────────────────────────────────────╮
│ Loaded seed: Python 3.12.10, FastAPI, OpenAI API, OpenSearch를 사용해 PDF 업로드·비동기 적재·벡터 검색·근거 기반 ... │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭───────── Info ─────────╮
│ Acceptance criteria: 7 │
╰────────────────────────╯
╭─────────── Info ───────────╮
│ Max decomposition depth: 2 │
╰────────────────────────────╯
╭───────── Info ──────────╮
│ Max parallel workers: 3 │
╰─────────────────────────╯
╭─────────── Info ────────────╮
│ Execution mode: fat_harness │
╰─────────────────────────────╯
╭──────────────────────────────────── Info ─────────────────────────────────────╮
│ Task worktree: /Users/a454676/.ouroboros/worktrees/rag_test/orch_5c0ab2ba2087 │
╰───────────────────────────────────────────────────────────────────────────────╯
╭─────────────── Info ───────────────╮
│ Task branch: ooo/orch_5c0ab2ba2087 │
╰────────────────────────────────────╯
╭────────── Info ──────────╮
│ Execution runtime: codex │
╰──────────────────────────╯

# 실행
uv run python -m pytest -q tests/test_ragger_replacement.py

# 일단 소스 실행 후 문제는 없었다.
# 작업 브랜치의 소스를 main 으로 병합해 온 후 소스 코드를 확인해 보자.
(worktress 경로에서) 
git add .
git commit -m "msg"
git status

# 원본 프로젝트로 이동
cd /Users/a454676/projects/rag_test
# 현재 브랜치 확인
git branch --show-current
# 현재 깃 상태 확인
git status
# 작업 경로가 clean 하다고 뜨면 ouroboros 가 만든 workbranch 를 병합해준다.
# 병합
git merge ooo/orch_5c0ab2ba2087

# 
deactivate
source .venv/bin/activate


# 터미널에서 시스템 패스 설정
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
## 참고로, .zshrc는 맥에서 zsh 터미널을 열 때마다 자동으로 읽는 개인 설정 파일이다.
# source ~/.zshrc : 새 터미널을 열지 않고도, 현재 터미널에서 다시 로드

# 전체 테스트 명령
uv run python -m pytest -q
## 테스트 명령을 수행하면, 프로젝트경로/tests/test_* 의 테스트 함수가 자동 실행된다.


# 무엇이 문제인지 모르겠다면, 다시 세션을 재개 해서, 디버깅을 추가해보자.
세션 id: orch_022540ba7182
# 
시드 파일
→ 해야 할 일

세션 ID
→ 실제로 진행했던 실행 기록

# Q. 인터뷰랑 세션은 어떻게 다른 걸까?
interview_...
→ 인터뷰 재개
→ 요구사항을 더 이야기하고 Seed를 만들거나 보완

orch_...
→ 실행 세션 재개
→ Seed를 바탕으로 진행하던 코드 작업을 이어서 수행

Ouroboros에서 말하는 Interview는 단순히 AI에게 작업을 부탁하는 대화가 아니라, 
요구사항을 정리해 Seed를 만드는 별도 단계

==> 다만,
기존 인터뷰가 이미 종료되어 Seed까지 생성된 상태에서 새로운 리팩터링 요구사항을 추가하려는 경우에는, 기존 인터뷰를 재개하는 것보다 새 인터뷰를 시작하는 편이 작업 구분에는 더 깔끔하다고 한다.



때문에, 지금
전체적인 공통 로거 구조나, 주석 처리 등 코드 구조를 재정의 하고 싶기 때문에,
새 세션을 생헝해서 작업해 준다.
-->
새 코드 공통 규칙을 정의 하고자 함
--> 
기존 세션을 이어가는게 아니라, 새 세션을 생성해서 새로운 seed 에 작업하도록 함..

``` 


uv tool install --force --with litellm 'ouroboros-ai[mcp]'