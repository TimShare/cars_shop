import logging


logger: logging.Logger | None = None
LOGGER_LEVEL = logging.INFO


def get_logger():
    """
    Возвращает глобальный логгер
    """
    global logger
    if not logger:
        logger = logging.getLogger()
        logger.setLevel(LOGGER_LEVEL)
        formatter = logging.Formatter(
            "| %(asctime)s | [%(levelname)s | %(filename)s:%(lineno)s] %(message)s"
        )
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger
