from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response, status

from app.logging_config import get_logger

app = FastAPI()
logger = get_logger(__name__)


@app.middleware("http")
async def log_unhandled_exceptions(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """처리되지 않은 요청 예외를 스택 트레이스와 함께 기록한다.

    Args:
        request: FastAPI가 전달한 현재 HTTP 요청이다.
        call_next: 요청을 다음 처리 단계로 전달하는 함수이다.

    Returns:
        다음 처리 단계가 만든 HTTP 응답이다.

    Raises:
        Exception: 처리되지 않은 예외를 기록한 뒤 FastAPI의 기본 오류 처리를
            유지하기 위해 다시 발생시킨다.
    """
    try:
        return await call_next(request)
    except Exception:
        logger.exception(
            "처리되지 않은 예외가 발생했습니다: %s %s",
            request.method,
            request.url.path,
        )
        raise


@app.get("/health", status_code=status.HTTP_200_OK)
def health() -> dict[str, str]:
    """애플리케이션이 정상 동작 중임을 나타내는 상태 정보를 반환한다."""
    logger.info("상태 확인 요청을 처리했습니다.")
    return {"status": "ok"}
