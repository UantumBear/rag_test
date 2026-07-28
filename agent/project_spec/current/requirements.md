# 현재 요구사항

- Python 3.12.10을 사용한다.
- 의존성은 uv, `pyproject.toml`, `uv.lock`으로 관리한다.
- FastAPI 애플리케이션은 `app/main.py`에서 제공한다.
- 애플리케이션 상태를 확인할 수 있는 `GET /health` 엔드포인트를 제공한다.
- 상태가 정상이면 HTTP 200과 `{"status": "ok"}`를 반환한다.
