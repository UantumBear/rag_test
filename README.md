# rag-test

Python 3.12.10과 FastAPI로 만든 간단한 애플리케이션입니다.

## 실행

```bash
uv run uvicorn app.main:app --reload
```

애플리케이션 실행 후 `GET http://127.0.0.1:8000/health`로 상태를 확인할 수 있습니다.

## 테스트

```bash
uv run python -m pytest -q
```
