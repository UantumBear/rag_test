# 현재 요구사항

- Python 3.12.10을 사용한다.
- 의존성은 uv, `pyproject.toml`, `uv.lock`으로 관리한다.
- FastAPI 애플리케이션은 `app/main.py`에서 제공한다.
- 애플리케이션 상태를 확인할 수 있는 `GET /health` 엔드포인트를 제공한다.
- 상태가 정상이면 HTTP 200과 `{"status": "ok"}`를 반환한다.
- 애플리케이션 모듈은 `app/logging_config.py`의 공통 로깅 설정을 사용한다.
- 처리되지 않은 요청 예외는 예외 정보와 스택 트레이스를 로그에 기록한다.
