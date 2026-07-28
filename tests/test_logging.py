import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.common.logger import HANDLER_NAME, LOG_FORMAT, LOG_LEVEL, get_logger
from app.main import log_unhandled_exceptions


def test_common_logger_uses_single_shared_configuration() -> None:
    first_logger = get_logger("app.first")
    second_logger = get_logger("app.second")
    common_logger = logging.getLogger("app")

    assert first_logger.parent is common_logger
    assert second_logger.parent is common_logger
    assert common_logger.level == LOG_LEVEL
    app_handlers = [
        handler for handler in common_logger.handlers if handler.name == HANDLER_NAME
    ]
    assert len(app_handlers) == 1
    assert app_handlers[0].formatter is not None
    assert app_handlers[0].formatter._fmt == LOG_FORMAT


def test_unhandled_exception_logs_stack_trace(monkeypatch) -> None:
    test_app = FastAPI()
    test_app.middleware("http")(log_unhandled_exceptions)

    @test_app.get("/error")
    def raise_error() -> None:
        raise RuntimeError("테스트 예외")

    logged_exceptions: list[tuple[str, tuple[object, ...]]] = []

    def record_exception(message: str, *args: object, **kwargs: object) -> None:
        logged_exceptions.append((message, args))

    monkeypatch.setattr("app.main.logger.exception", record_exception)

    with TestClient(test_app, raise_server_exceptions=False) as client:
        response = client.get("/error")

    assert response.status_code == 500
    assert logged_exceptions == [
        (
            "처리되지 않은 예외가 발생했습니다: %s %s",
            ("GET", "/error"),
        )
    ]
