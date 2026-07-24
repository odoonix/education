
import functools
import logging
import time

logger = logging.getLogger(__name__)


def retry(max_attempts: int = 3, base_delay: float = 1.0, exceptions: tuple = (Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt >= max_attempts:
                        logger.error(
                            "retry_exhausted: function=%s attempts=%d error=%s",
                            func.__name__, attempt, exc,
                        )
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        "retry_attempt: function=%s attempt=%d/%d delay=%.1fs error=%s",
                        func.__name__, attempt, max_attempts, delay, exc,
                    )
                    time.sleep(delay)
                    attempt += 1
        return wrapper
    return decorator