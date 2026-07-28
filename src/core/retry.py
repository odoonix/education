"""
Retry Decorator: وقتی یک تابع به یه دلیل موقتی (مثلاً قطعی لحظه‌ای شبکه) خطا
میده، به‌جای اینکه فوری شکست بخوریم، چندبار با یه مکث بین هر تلاش دوباره
امتحان می‌کنیم. مکث هر بار بیشتر میشه (Exponential Backoff) که فشار زیادی
هم به سرور مقصد وارد نکنیم.

مثال: delay=1, backoff=2, times=3
  تلاش ۱ شکست -> ۱ ثانیه صبر
  تلاش ۲ شکست -> ۲ ثانیه صبر
  تلاش ۳ شکست -> دیگه تلاش نمی‌کنیم، خطا رو بالا می‌فرستیم
"""

import functools
import logging
import time
from typing import Tuple, Type

logger = logging.getLogger(__name__)

# خطاهایی که تحت هیچ شرایطی نباید retry بشن -- این‌ها خطاهای منطقی/برنامه‌نویسی
# هستن (نه مشکل موقتی شبکه)، پس retry کردنشون فقط وقت تلف می‌کنه و نتیجه
# همیشه یکی می‌مونه.
NON_RETRYABLE_EXCEPTIONS = (
    KeyboardInterrupt,
    SystemExit,
    TypeError,
    ValueError,
    KeyError,
    AttributeError,
    IndexError,
)


def retry(
    times: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    max_delay: float = 30.0,  # سقف زمان انتظار بین تلاش‌ها (به ثانیه)
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except NON_RETRYABLE_EXCEPTIONS as exc:
                    logger.error(f"خطای غیرقابل بازتلاش در {func.__name__}: {exc}")
                    raise
                except exceptions as exc:
                    if attempt == times:
                        logger.error(
                            f"{func.__name__} بعد از {times} تلاش شکست خورد: {exc}"
                        )
                        raise
                    logger.warning(
                        f"تلاش {attempt}/{times} برای {func.__name__} شکست خورد: "
                        f"{exc} — {current_delay:.1f}s صبر می‌کنیم و دوباره امتحان می‌کنیم..."
                    )
                    time.sleep(current_delay)
                    current_delay = min(current_delay * backoff, max_delay)
        return wrapper
    return decorator
