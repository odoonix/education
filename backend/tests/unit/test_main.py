"""
Tests for app.main: _run_once logic and loop/graceful shutdown behavior,
without needing real Odoo or database (run_full_sync is fully mocked).

Note: Settings is a dataclass(frozen=True), so we cannot directly monkeypatch
a field on it; instead, we replace the entire settings object with a new
version using dataclasses.replace.
"""
import dataclasses

import app.main as main_module


def _settings_with(**overrides):
    return main_module.settings.model_copy(update=overrides)

def test_run_once_returns_true_on_success(monkeypatch):
    monkeypatch.setattr(main_module, "run_full_sync", lambda: {"fetched": 1})
    assert main_module._run_once() is True


def test_run_once_returns_false_on_exception(monkeypatch):
    def _boom():
        raise RuntimeError("odoo down")

    monkeypatch.setattr(main_module, "run_full_sync", _boom)
    assert main_module._run_once() is False


def test_main_once_mode_exits_zero_on_success(monkeypatch):
    monkeypatch.setattr(main_module, "settings", _settings_with(run_mode="once"))
    monkeypatch.setattr(main_module, "run_full_sync", lambda: {"fetched": 1})
    monkeypatch.setattr(main_module, "setup_logging", lambda level: None)

    exited_with = {}

    def fake_exit(code):
        exited_with["code"] = code
        raise SystemExit(code)

    monkeypatch.setattr(main_module.sys, "exit", fake_exit)

    try:
        main_module.main()
    except SystemExit:
        pass

    assert exited_with["code"] == 0


def test_main_once_mode_exits_nonzero_on_failure(monkeypatch):
    monkeypatch.setattr(main_module, "settings", _settings_with(run_mode="once"))

    def _boom():
        raise RuntimeError("boom")

    monkeypatch.setattr(main_module, "run_full_sync", _boom)
    monkeypatch.setattr(main_module, "setup_logging", lambda level: None)

    exited_with = {}

    def fake_exit(code):
        exited_with["code"] = code
        raise SystemExit(code)

    monkeypatch.setattr(main_module.sys, "exit", fake_exit)

    try:
        main_module.main()
    except SystemExit:
        pass

    assert exited_with["code"] == 1


def test_main_loop_mode_stops_gracefully_on_shutdown_signal(monkeypatch):
    monkeypatch.setattr(
        main_module, "settings", _settings_with(run_mode="loop", sync_interval_seconds=5)
    )
    monkeypatch.setattr(main_module, "setup_logging", lambda level: None)
    monkeypatch.setattr(main_module.signal, "signal", lambda *a, **k: None)

    run_count = {"n": 0}

    def fake_run_once():
        run_count["n"] += 1
        main_module._shutdown_requested = True
        return True

    monkeypatch.setattr(main_module, "_run_once", fake_run_once)
    monkeypatch.setattr(main_module.time, "sleep", lambda s: None)

    exited_with = {}

    def fake_exit(code):
        exited_with["code"] = code
        raise SystemExit(code)

    monkeypatch.setattr(main_module.sys, "exit", fake_exit)

    try:
        main_module.main()
    except SystemExit:
        pass
    finally:
        main_module._shutdown_requested = False

    assert run_count["n"] == 1
    assert exited_with["code"] == 0
