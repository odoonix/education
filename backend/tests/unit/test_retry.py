"""
Tests for the retry decorator.
We monkeypatch the actual time.sleep so tests run instantly (without waiting
real seconds) while also checking that the delay backoff works correctly.
"""
import pytest

from app.retry import retry


class FlakyError(Exception):
    pass


def test_succeeds_immediately_without_retry():
    calls = {"count": 0}

    @retry(max_attempts=3, initial_delay=0)
    def always_ok():
        calls["count"] += 1
        return "ok"

    assert always_ok() == "ok"
    assert calls["count"] == 1


def test_retries_then_succeeds(monkeypatch):
    sleep_calls = []
    monkeypatch.setattr("app.retry.time.sleep", lambda s: sleep_calls.append(s))

    calls = {"count": 0}

    @retry(max_attempts=3, initial_delay=1.0, backoff_factor=2.0, exceptions=(FlakyError,))
    def fails_twice_then_ok():
        calls["count"] += 1
        if calls["count"] < 3:
            raise FlakyError("temporary")
        return "ok"

    result = fails_twice_then_ok()

    assert result == "ok"
    assert calls["count"] == 3
    assert sleep_calls == [1.0, 2.0]


def test_raises_after_max_attempts(monkeypatch):
    monkeypatch.setattr("app.retry.time.sleep", lambda s: None)

    calls = {"count": 0}

    @retry(max_attempts=3, initial_delay=0.1, exceptions=(FlakyError,))
    def always_fails():
        calls["count"] += 1
        raise FlakyError("permanent failure")

    with pytest.raises(FlakyError):
        always_fails()

    assert calls["count"] == 3


def test_does_not_retry_unlisted_exceptions(monkeypatch):
    monkeypatch.setattr("app.retry.time.sleep", lambda s: None)
    calls = {"count": 0}

    @retry(max_attempts=3, initial_delay=0.1, exceptions=(FlakyError,))
    def raises_other_error():
        calls["count"] += 1
        raise ValueError("not retryable")

    with pytest.raises(ValueError):
        raises_other_error()

    assert calls["count"] == 1
