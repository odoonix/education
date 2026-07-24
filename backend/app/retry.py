import functools
import logging
import time
from typing import Tuple, Type

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt >= max_attempts:
                        logger.error(
                            "operation %s failed after %s attempts: %s",
                            func.__name__,
                            attempt,
                            exc,
                        )
                        raise
                    logger.warning(
                        "trying %s/%s operation %s failed (%s); retrying in %.1f seconds",
                        attempt,
                        max_attempts,
                        func.__name__,
                        exc,
                        delay,
                    )
                    time.sleep(delay)
                    delay *= backoff_factor
                    attempt += 1

        return wrapper

    return decorator
