# 현재 아키텍처

## 파일 구조

```text
app/
├── __init__.py
├── common/
│   ├── __init__.py
│   └── logger.py
└── main.py

tests/
├── test_health.py
└── test_logging.py
```

## 모듈 책임

- `app/common/logger.py`: 애플리케이션 공통 로그 레벨, 형식, 표준 오류
  스트림 핸들러를 한 곳에서 설정하고 모듈별 자식 로거를 제공한다.
- `app/main.py`: 공통 로거를 사용하며, 처리되지 않은 요청 예외를 기록하는
  HTTP 미들웨어와 상태 확인 엔드포인트를 정의한다.
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

## 공통 로거 구조

공통 로거는 여러 애플리케이션 모듈에서 함께 사용할 수 있도록
`app/common/logger.py`에 두고 설정 책임을 `app/main.py`에서 분리한다.

`app.common.logger`만 로그 레벨, 로그 형식, 표준 오류 스트림 핸들러를
설정한다. 각 기능 모듈은 핸들러나 포매터를 직접 만들지 않고
`get_logger(__name__)`으로 `app` 이름 공간 아래의 자식 로거를 사용한다.
공통 핸들러에는 고유 이름을 부여해 설정 함수가 여러 번 호출되어도 같은
핸들러가 중복 추가되지 않는다.
