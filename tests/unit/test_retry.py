from src.core.retry import retry


def test_retry_succeeds_after_transient_failures():
    """تابع ۲ بار شکست می‌خوره و بار سوم موفق میشه؛ retry باید همین رفتار رو تحمل کنه.
    از ConnectionError استفاده می‌کنیم (نه ValueError) چون ValueError جزو
    NON_RETRYABLE_EXCEPTIONS هست و طبق طراحی هیچ‌وقت retry نمیشه."""
    calls = {"count": 0}

    @retry(times=3, delay=0, backoff=1, exceptions=(ConnectionError,))
    def flaky():
        calls["count"] += 1
        if calls["count"] < 3:
            raise ConnectionError("قطعی موقت شبکه")
        return "OK"

    result = flaky()

    assert result == "OK"
    assert calls["count"] == 3


def test_retry_raises_after_exhausting_all_attempts():
    """اگه بعد از همه‌ی تلاش‌ها بازم شکست بخوره، خطای اصلی باید بالا بره."""
    calls = {"count": 0}

    @retry(times=2, delay=0, backoff=1, exceptions=(ConnectionError,))
    def always_fails():
        calls["count"] += 1
        raise ConnectionError("همیشه شکست می‌خوره")

    try:
        always_fails()
        assert False, "باید ConnectionError raise می‌شد"
    except ConnectionError:
        pass

    assert calls["count"] == 2  # دقیقاً به تعداد times تلاش کرد، نه بیشتر


def test_retry_does_not_catch_unrelated_exceptions():
    """اگه نوع خطا تو لیست exceptions نباشه (و NON_RETRYABLE هم نباشه)، اصلاً retry نمی‌کنه."""
    calls = {"count": 0}

    @retry(times=3, delay=0, backoff=1, exceptions=(ConnectionError,))
    def raises_runtime_error():
        calls["count"] += 1
        raise RuntimeError("این نوع خطا تو لیست exceptions نیست")

    try:
        raises_runtime_error()
        assert False, "باید RuntimeError raise می‌شد"
    except RuntimeError:
        pass

    assert calls["count"] == 1  # فقط یک‌بار تلاش کرد


def test_retry_never_retries_logical_errors_even_if_explicitly_listed():
    """
    نکته‌ی مهم طراحی: حتی اگه صراحتاً بگی exceptions=(ValueError,)، چون
    ValueError جزو NON_RETRYABLE_EXCEPTIONS هست، اصلاً retry نمیشه -- چون
    این‌جور خطاها معمولاً یعنی باگ تو کد، نه مشکل موقتی شبکه، و retry
    کردنشون فقط وقت تلف می‌کنه.
    """
    calls = {"count": 0}

    @retry(times=3, delay=0, backoff=1, exceptions=(ValueError,))
    def raises_value_error():
        calls["count"] += 1
        raise ValueError("این یه خطای منطقیه، نه شبکه‌ای")

    try:
        raises_value_error()
        assert False, "باید ValueError raise می‌شد"
    except ValueError:
        pass

    assert calls["count"] == 1  # فقط یک‌بار تلاش کرد، هیچ retry‌ای انجام نشد
