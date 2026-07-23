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