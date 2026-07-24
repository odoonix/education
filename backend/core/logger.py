
import json
import logging
import sys
from datetime import datetime, timezone

from core.config import get_settings

_STANDARD_ATTRS = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys())


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # فیلدهای extra (مثل operation, total_records, ...) رو هم اضافه می‌کنیم
        for key, value in record.__dict__.items():
            if key not in _STANDARD_ATTRS and key != "message":
                log_data[key] = value

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)


def configure_logging() -> None:
    settings = get_settings()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))


def get_logger(name: str = "app") -> logging.Logger:
    return logging.getLogger(name)