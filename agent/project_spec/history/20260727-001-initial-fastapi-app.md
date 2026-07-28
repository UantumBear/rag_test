```bash

@agent/project_spec/change_request.md 
해당 파일은 새로운 요구사항 문서 이다.

```

slug: initial-fastapi-app

# 간단한 FastAPI 앱 생성

## 변경 요구사항

빈 프로젝트에 간단한 FastAPI 애플리케이션을 구현한다.

- Python 3.12.10을 사용한다.
- uv와 pyproject.toml로 의존성을 관리한다.
- FastAPI 애플리케이션은 app/main.py에 구현한다.
- GET /health 엔드포인트를 제공한다.
- GET /health는 HTTP 200과 다음 JSON을 반환한다.

```json
{
  "status": "ok"
}

