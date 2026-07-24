import pytest

from core.retry import retry


def test_retry_succeeds_after_transient_failures(mocker):
    mock_sleep = mocker.patch("core.retry.time.sleep")  # صبر واقعی نمی‌کنیم، تست سریع بمونه

    call_count = {"n": 0}

    @retry(max_attempts=3, base_delay=1.0, exceptions=(ConnectionError,))
    def flaky_function():
        call_count["n"] += 1
        if call_count["n"] < 3:
            raise ConnectionError("temporary network issue")
        return "success"

    result = flaky_function()

    assert result == "success"
    assert call_count["n"] == 3          # دو بار fail شده، سومین بار موفق
    assert mock_sleep.call_count == 2    # بین تلاش‌ها صبر کرده (نه بعد از موفقیت)


def test_retry_raises_after_max_attempts_exhausted(mocker):
    mocker.patch("core.retry.time.sleep")

    @retry(max_attempts=3, base_delay=1.0, exceptions=(ConnectionError,))
    def always_fails():
        raise ConnectionError("permanent network issue")

    with pytest.raises(ConnectionError, match="permanent network issue"):
        always_fails()


def test_retry_does_not_catch_unlisted_exceptions(mocker):
    """خطاهایی که تو exceptions لیست نشدن، باید فوراً raise بشن، بدون retry."""
    mock_sleep = mocker.patch("core.retry.time.sleep")

    @retry(max_attempts=3, base_delay=1.0, exceptions=(ConnectionError,))
    def raises_value_error():
        raise ValueError("this is not a transient error")

    with pytest.raises(ValueError):
        raises_value_error()

    mock_sleep.assert_not_called()   # اصلاً retry نباید بشه