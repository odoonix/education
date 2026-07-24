from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from xmlrpc.client import ServerProxy

NAMESPACE = "odoo_sync_seed"


@dataclass(frozen=True)
class Config:
    url: str = os.getenv("ODOO_URL", "http://odoo:8069")
    database: str = os.getenv("ODOO_DATABASE", "odoo")
    username: str = os.getenv("ODOO_USERNAME", "admin")
    password: str = os.getenv("ODOO_PASSWORD", "admin")


CONTACTS = [
    ("contact_01", {"name": "Sync Contact 01", "email": "contact01@example.test", "phone": "+1-555-0101", "mobile": "+1-555-1101"}),
    ("contact_02", {"name": "Sync Contact 02", "email": "contact02@example.test", "phone": "+1-555-0102", "mobile": "+1-555-1102"}),
    ("contact_03", {"name": "Sync Contact 03", "email": "contact03@example.test", "phone": "+1-555-0103", "mobile": "+1-555-1103"}),
    ("contact_04", {"name": "Sync Contact 04", "email": "contact04@example.test", "phone": "+1-555-0104", "mobile": "+1-555-1104"}),
    ("contact_05", {"name": "Sync Contact 05", "email": "contact05@example.test", "phone": "+1-555-0105", "mobile": "+1-555-1105"}),
]
PRODUCTS = [
    ("product_01", {"name": "Sync Product 01", "default_code": "SYNC-P01", "list_price": 10.0, "detailed_type": "consu"}),
    ("product_02", {"name": "Sync Product 02", "default_code": "SYNC-P02", "list_price": 20.0, "detailed_type": "consu"}),
    ("product_03", {"name": "Sync Product 03", "default_code": "SYNC-P03", "list_price": 30.0, "detailed_type": "consu"}),
    ("product_04", {"name": "Sync Product 04", "default_code": "SYNC-P04", "list_price": 40.0, "detailed_type": "service"}),
    ("product_05", {"name": "Sync Product 05", "default_code": "SYNC-P05", "list_price": 50.0, "detailed_type": "service"}),
]
ORDERS = [
    ("order_draft", "contact_01", "draft", "2026-07-20 10:00:00"),
    ("order_confirmed", "contact_02", "sale", "2026-07-21 10:00:00"),
    ("order_cancelled", "contact_03", "cancel", "2026-07-22 10:00:00"),
]
LINES = [
    ("line_01", "order_draft", "product_01", 1, 10.0),
    ("line_02", "order_draft", "product_02", 2, 20.0),
    ("line_03", "order_confirmed", "product_03", 3, 30.0),
    ("line_04", "order_confirmed", "product_04", 4, 40.0),
    ("line_05", "order_cancelled", "product_05", 5, 50.0),
    ("line_06", "order_cancelled", "product_01", 6, 10.0),
]


class Odoo:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.common = ServerProxy(f"{config.url}/xmlrpc/2/common", allow_none=True)
        self.object = ServerProxy(f"{config.url}/xmlrpc/2/object", allow_none=True)
        uid = self.common.authenticate(config.database, config.username, config.password, {})
        if not isinstance(uid, int):
            raise RuntimeError("Odoo authentication failed")
        self.uid = uid

    def call(self, model: str, method: str, *args: Any, **kwargs: Any) -> Any:
        return self.object.execute_kw(
            self.config.database,
            self.uid,
            self.config.password,
            model,
            method,
            list(args),
            kwargs,
        )

    def ref(self, xml_id: str) -> int | None:
        rows = self.call("ir.model.data", "search_read", [["module", "=", NAMESPACE], ["name", "=", xml_id]], fields=["res_id"], limit=1)
        return int(rows[0]["res_id"]) if rows else None

    def ensure_xml_id(self, name: str, model: str, res_id: int) -> None:
        existing = self.call("ir.model.data", "search", [["module", "=", NAMESPACE], ["name", "=", name]], limit=1)
        values = {"module": NAMESPACE, "name": name, "model": model, "res_id": res_id, "noupdate": True}
        if existing:
            self.call("ir.model.data", "write", existing, values)
        else:
            self.call("ir.model.data", "create", values)

    def upsert(self, xml_id: str, model: str, values: dict[str, Any]) -> int:
        res_id = self.ref(xml_id)
        if res_id is None:
            res_id = int(self.call(model, "create", values))
            self.ensure_xml_id(xml_id, model, res_id)
        else:
            self.call(model, "write", [res_id], values)
        return res_id


def seed() -> None:
    odoo = Odoo(Config())
    ids: dict[str, int] = {}
    for xml_id, values in CONTACTS:
        ids[xml_id] = odoo.upsert(xml_id, "res.partner", values)
    for xml_id, values in PRODUCTS:
        ids[xml_id] = odoo.upsert(xml_id, "product.product", values)
    for xml_id, contact_xml_id, state, order_date in ORDERS:
        order_id = odoo.upsert(xml_id, "sale.order", {"partner_id": ids[contact_xml_id], "date_order": order_date})
        ids[xml_id] = order_id
    for xml_id, order_xml_id, product_xml_id, qty, price in LINES:
        line_id = odoo.ref(xml_id)
        values = {
            "order_id": ids[order_xml_id],
            "product_id": ids[product_xml_id],
            "product_uom_qty": qty,
            "price_unit": price,
        }
        if line_id is None:
            line_id = int(odoo.call("sale.order.line", "create", values))
            odoo.ensure_xml_id(xml_id, "sale.order.line", line_id)
        else:
            try:
                odoo.call("sale.order.line", "write", [line_id], values)
            except Exception:
                pass
        ids[xml_id] = line_id
    for xml_id, _contact_xml_id, state, _order_date in ORDERS:
        order_id = ids[xml_id]
        current = odoo.call("sale.order", "read", [order_id], ["state"])[0]["state"]
        if state == "sale" and current == "draft":
            odoo.call("sale.order", "action_confirm", [order_id])
        elif state == "cancel" and current != "cancel":
            if current == "draft":
                odoo.call("sale.order", "action_confirm", [order_id])
            odoo.call("sale.order", "action_cancel", [order_id])
            current = odoo.call("sale.order", "read", [order_id], ["state"])[0]["state"]
            if current != "cancel":
                odoo.call("sale.order", "write", [order_id], {"state": "cancel"})
    verify()
    print("seed completed")


def verify() -> None:
    odoo = Odoo(Config())
    expected = [x[0] for x in CONTACTS + PRODUCTS + [(o[0], {}) for o in ORDERS] + [(l[0], {}) for l in LINES]]
    missing = [xml_id for xml_id in expected if odoo.ref(xml_id) is None]
    if missing:
        raise RuntimeError(f"missing controlled records: {', '.join(missing)}")
    states = {xml_id: state for xml_id, _contact, state, _date in ORDERS}
    for xml_id, state in states.items():
        order_id = odoo.ref(xml_id)
        current = odoo.call("sale.order", "read", [order_id], ["state"])[0]["state"]
        if current != state:
            raise RuntimeError(f"{xml_id} expected state {state}, got {current}")
    print("seed verification passed: 19 controlled records")


def main(argv: list[str]) -> int:
    try:
        if len(argv) != 2 or argv[1] not in {"seed", "verify"}:
            print("usage: seed_odoo.py seed|verify", file=sys.stderr)
            return 2
        if argv[1] == "seed":
            seed()
        else:
            verify()
        return 0
    except Exception as exc:
        print(f"seed failure: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
