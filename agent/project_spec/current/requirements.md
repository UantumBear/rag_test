# 현재 요구사항

- Python 3.12.10을 사용한다.
- 의존성은 uv, `pyproject.toml`, `uv.lock`으로 관리한다.
- FastAPI 애플리케이션은 `app/main.py`에서 제공한다.
- 애플리케이션 상태를 확인할 수 있는 `GET /health` 엔드포인트를 제공한다.
- 상태가 정상이면 HTTP 200과 `{"status": "ok"}`를 반환한다.
- 애플리케이션 모듈은 `app/common/logger.py`의 공통 로깅 설정을 사용한다.
- 처리되지 않은 요청 예외는 예외 정보와 스택 트레이스를 로그에 기록한다.
- `POST /chat` 엔드포인트로 일반 질문을 받아 OpenAI LLM의 텍스트 답변을
  반환한다.
- 질문은 1자 이상 4000자 이하의 문자열이어야 한다.
- 질문 처리는 LangChain의 메시지·모델 인터페이스와 LangGraph의 상태
  그래프를 사용하며, RAG 검색과 대화 기록은 포함하지 않는다.
- OpenAI API 키는 `OPENAI_API_KEY`, 모델 이름은 `OPENAI_MODEL` 환경
  변수로 설정한다. 모델 이름의 기본값은 `gpt-4o-mini`이다.
