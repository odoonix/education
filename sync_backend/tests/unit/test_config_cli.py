from __future__ import annotations

import pytest

from odoo_sync.cli import build_parser
from odoo_sync.domain.pagination import MAX_PAGE_SIZE, PageSize

pytestmark = pytest.mark.unit


def test_page_size_bounds_are_enforced() -> None:
    PageSize(1)
    PageSize(MAX_PAGE_SIZE)
    with pytest.raises(ValueError):
        PageSize(0)


def test_cli_accepts_required_sync_modes() -> None:
    parser = build_parser()
    args = parser.parse_args(["sync", "--full", "--page-size", "2"])
    assert args.full is True
    assert args.page_size == 2
