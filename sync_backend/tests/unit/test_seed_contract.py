from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def test_seed_dataset_has_required_deterministic_size() -> None:
    path = Path(__file__).parents[3] / "docker" / "odoo" / "seed_odoo.py"
    spec = importlib.util.spec_from_file_location("seed_odoo", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["seed_odoo"] = module
    spec.loader.exec_module(module)

    assert len(module.CONTACTS) == 5
    assert len(module.PRODUCTS) == 5
    assert len(module.ORDERS) == 3
    assert len(module.LINES) == 6
    assert module.NAMESPACE == "odoo_sync_seed"
