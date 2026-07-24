import logging

from core.logger import configure_logging, get_logger


def test_get_logger_returns_logger_instance():
    logger = get_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"


def test_configure_logging_runs_without_error():
    configure_logging()  # فقط چک می‌کنیم خطا نمی‌ده