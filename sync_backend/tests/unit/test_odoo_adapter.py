from __future__ import annotations

from typing import Any

import pytest

from odoo_sync.infrastructure.odoo.adapter import OdooAdapter

pytestmark = pytest.mark.unit


class FakeClient:
    def __init__(self) -> None:
        self.domains: list[list[Any]] = []

    def search_read(
        self, model: str, domain: list[Any], fields: list[str], *, limit: int, order: str = "id asc"
    ) -> list[dict[str, Any]]:
        self.domains.append(domain)
        if len(self.domains) == 1:
            return [
                {
                    "id": 1,
                    "name": "A",
                    "email": False,
                    "phone": False,
                    "mobile": False,
                    "write_date": False,
                },
                {
                    "id": 2,
                    "name": False,
                    "email": False,
                    "phone": False,
                    "mobile": False,
                    "write_date": False,
                },
            ]
        if len(self.domains) == 2:
            return [
                {
                    "id": 3,
                    "name": "C",
                    "email": False,
                    "phone": False,
                    "mobile": False,
                    "write_date": False,
                }
            ]
        return []


def test_adapter_keyset_pagination_advances_after_mapping_error() -> None:
    client = FakeClient()
    records = list(OdooAdapter(client).iter_contacts(page_size=2, lower=None, upper=None))  # type: ignore[arg-type]

    assert [r.raw_id for r in records] == [1, 2, 3]
    assert records[1].is_error
    assert client.domains[1][0] == ["id", ">", 2]
