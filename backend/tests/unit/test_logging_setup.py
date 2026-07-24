import json
import logging

from app.logging_setup import JsonFormatter, setup_logging


class TestJsonFormatter:
    def test_formats_basic_record_as_valid_json(self):
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="hello %s",
            args=("world",),
            exc_info=None,
        )

        output = formatter.format(record)
        parsed = json.loads(output)

        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test.logger"
        assert parsed["message"] == "hello world"
        assert "timestamp" in parsed

    def test_includes_exception_info_when_present(self):
        formatter = JsonFormatter()
        try:
            raise ValueError("boom")
        except ValueError:
            import sys

            record = logging.LogRecord(
                name="test.logger",
                level=logging.ERROR,
                pathname=__file__,
                lineno=1,
                msg="failed",
                args=(),
                exc_info=sys.exc_info(),
            )

        output = formatter.format(record)
        parsed = json.loads(output)
        assert "exception" in parsed
        assert "ValueError" in parsed["exception"]


class TestSetupLogging:
    def test_setup_logging_sets_level_and_json_handler(self):
        setup_logging("DEBUG")
        root = logging.getLogger()

        assert root.level == logging.DEBUG
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0].formatter, JsonFormatter)

    def test_calling_setup_logging_twice_does_not_duplicate_handlers(self):
        setup_logging("INFO")
        setup_logging("INFO")
        root = logging.getLogger()
        assert len(root.handlers) == 1
