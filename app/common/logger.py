import logging
import sys

LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOGGER_NAME = "app"
HANDLER_NAME = "app.stderr"


def configure_logging() -> None:
    """애플리케이션 공통 로그 레벨, 형식, 출력 핸들러를 설정한다.

    매개변수와 반환값은 없으며, 이미 설정된 경우 핸들러를 다시 추가하지 않는다.
    """
    logger = logging.getLogger(LOGGER_NAME)
    if any(handler.name == HANDLER_NAME for handler in logger.handlers):
        return

    handler = logging.StreamHandler(sys.stderr)
    handler.set_name(HANDLER_NAME)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger.setLevel(LOG_LEVEL)
    logger.addHandler(handler)
    logger.propagate = False


def get_logger(module_name: str) -> logging.Logger:
    """공통 설정을 사용하는 모듈별 로거를 반환한다.

    Args:
        module_name: 일반적으로 ``__name__``으로 전달하는 모듈 이름이다.

    Returns:
        공통 ``app`` 로거 아래에서 동작하는 자식 로거이다.
    """
    configure_logging()
    return logging.getLogger(module_name)
