# tests/test_core/test_shutdown_handler.py

import signal

from core.shutdown import ShutdownHandler


def test_shutdown_handler_initial_state():
    handler = ShutdownHandler()

    assert handler.shutdown_requested is False


def test_shutdown_handler_sets_flag_when_signal_received():
    handler = ShutdownHandler()

    handler._handle_signal(signal.SIGTERM, None)

    assert handler.shutdown_requested is True


def test_shutdown_handler_sets_flag_for_sigint():
    handler = ShutdownHandler()

    handler._handle_signal(signal.SIGINT, None)

    assert handler.shutdown_requested is True