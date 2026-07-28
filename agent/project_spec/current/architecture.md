# 현재 아키텍처

## 파일 구조

```text
app/
├── __init__.py
└── main.py

tests/
└── test_health.py
```

## 모듈 책임

- `app/main.py`: FastAPI 인스턴스와 상태 확인 엔드포인트를 정의한다.
- `tests/test_health.py`: 상태 확인 API의 정상 응답과 지원하지 않는 HTTP 메서드 처리를 검증한다.

## 요청 처리 흐름

Uvicorn이 `app.main:app`을 로드하고, FastAPI가 `GET /health` 요청을 `health` 함수로 전달해 상태 JSON을 반환한다.
