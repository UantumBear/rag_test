# 현재 아키텍처

## 파일 구조

```text
app/
├── __init__.py
├── api/
│   ├── __init__.py
│   └── chat.py
├── common/
│   ├── __init__.py
│   └── logger.py
├── models/
│   ├── __init__.py
│   └── chat.py
├── services/
│   ├── __init__.py
│   └── chat.py
└── main.py

tests/
├── test_chat.py
├── test_health.py
└── test_logging.py
```

## 모듈 책임

- `app/common/logger.py`: 애플리케이션 공통 로그 레벨, 형식, 표준 오류
  스트림 핸들러를 한 곳에서 설정하고 모듈별 자식 로거를 제공한다.
- `app/models/chat.py`: 채팅 API 질문과 답변의 Pydantic 모델 및 질문 길이
  검증 규칙을 정의한다.
- `app/services/chat.py`: OpenAI 채팅 모델을 생성하고, 한 단계 LangGraph를
  컴파일해 일반 질문을 처리하는 `ChatService`를 제공한다. 공용 서비스
  인스턴스는 최초 요청 때 한 번 생성해 재사용한다.
- `app/api/chat.py`: 채팅 서비스 의존성을 연결하고 `POST /chat` 요청과
  응답을 처리한다.
- `app/main.py`: 공통 로거를 사용하며, 처리되지 않은 요청 예외를 기록하는
  HTTP 미들웨어, 채팅 라우터와 상태 확인 엔드포인트를 연결한다.
- `tests/test_chat.py`: LLM을 테스트 대역으로 교체해 질문 전달, 입력 검증,
  환경 설정 오류 처리를 검증한다.
- `tests/test_health.py`: 상태 확인 API의 정상 응답과 지원하지 않는 HTTP 메서드 처리를 검증한다.
- `tests/test_logging.py`: 공통 설정의 중복 방지와 처리되지 않은 예외의 로그
  기록을 검증한다.

## 요청 처리 흐름

Uvicorn이 `app.main:app`을 로드하면 `app.main`은
`app.common.logger.get_logger(__name__)`로 공통 설정을 사용하는 자식 로거를
가져온다. FastAPI의 로깅 미들웨어가 요청을 다음 처리 단계로 전달하고,
`GET /health` 요청은 `health` 함수가 상태 JSON을 반환한다.

요청 처리 중 애플리케이션에서 처리되지 않은 예외가 발생하면 미들웨어가
`logger.exception()`으로 요청 메서드, 경로, 예외 정보와 스택 트레이스를
기록한 뒤 예외를 다시 발생시킨다. 따라서 FastAPI의 기존 오류 응답 처리는
그대로 유지된다.

## 채팅 요청 처리 흐름

`POST /chat`은 `ChatRequest`로 질문 길이를 검증한 뒤 `ChatService.ask()`를
호출한다. 서비스는 애플리케이션 수명 동안 재사용되는 컴파일된 LangGraph에
질문 상태를 전달한다. 그래프의 `generate_answer` 노드는 질문을 LangChain
`HumanMessage`로 변환하고 `ChatOpenAI`를 한 번 호출한 뒤 문자열 답변을
상태에 저장한다. API는 그 값을 `ChatResponse`로 반환한다.

현재 그래프는 일반 LLM 호출 노드 하나만 포함한다. 서비스와 API 사이의
의존성 경계를 유지하므로 이후 검색이나 후처리 노드를 추가할 때 HTTP 계약을
변경하지 않고 그래프 내부를 확장할 수 있다. 대화 상태 저장소나 RAG 검색은
현재 범위에 포함하지 않는다.

## 공통 로거 구조

공통 로거는 여러 애플리케이션 모듈에서 함께 사용할 수 있도록
`app/common/logger.py`에 두고 설정 책임을 `app/main.py`에서 분리한다.

`app.common.logger`만 로그 레벨, 로그 형식, 표준 오류 스트림 핸들러를
설정한다. 각 기능 모듈은 핸들러나 포매터를 직접 만들지 않고
`get_logger(__name__)`으로 `app` 이름 공간 아래의 자식 로거를 사용한다.
공통 핸들러에는 고유 이름을 부여해 설정 함수가 여러 번 호출되어도 같은
핸들러가 중복 추가되지 않는다.
