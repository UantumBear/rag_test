# rag-test

Python 3.12.10과 FastAPI로 만든 간단한 애플리케이션입니다.

## 환경 설정

환경변수는 .env 경로에 위치해 있습니다.

`.env`을 참고해 OpenAI API 키를 환경 변수로 설정합니다.
OPENAI_API_KEY
OPENAI_MODEL

`OPENAI_MODEL`은 생략할 수 있으며 기본값은 `gpt-4o-mini`입니다.

## 실행

```bash
uv run uvicorn app.main:app --reload
```

애플리케이션 실행 후 `GET http://127.0.0.1:8000/health`로 상태를 확인할 수 있습니다.
일반 질문은 다음과 같이 전달할 수 있습니다.

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"한국의 수도는 어디인가요?"}'
```

## 테스트

```bash
uv run python -m pytest -q
```
