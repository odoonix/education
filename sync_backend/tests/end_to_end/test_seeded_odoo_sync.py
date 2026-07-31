from __future__ import annotations

import subprocess

import pytest

pytestmark = pytest.mark.end_to_end


def test_seed_verify_script_runs_in_compose_environment() -> None:
    result = subprocess.run(
        ["python3", "/seed/seed_odoo.py", "verify"], check=False, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    assert "19 controlled records" in result.stdout
