import xmlrpc.client
from typing import Any

from backend.adapters.base import ErpAdapter


class OdooConnectionError(Exception):
    pass


class OdooAdapter(ErpAdapter):
    def __init__(self, url: str, db: str, username: str, password: str) -> None:
        self._url = url
        self._db = db
        self._username = username
        self._password = password
        self._uid: int | None = None
        self._models: xmlrpc.client.ServerProxy | None = None

    def connect(self) -> None:
        common = xmlrpc.client.ServerProxy(f"{self._url}/xmlrpc/2/common")
        try:
            uid = common.authenticate(self._db, self._username, self._password, {})
        except (xmlrpc.client.Fault, OSError) as exc:
            raise OdooConnectionError(f"Failed to authenticate with Odoo: {exc}") from exc

        if not uid:
            raise OdooConnectionError("Odoo authentication rejected, check credentials")

        self._uid = uid
        self._models = xmlrpc.client.ServerProxy(f"{self._url}/xmlrpc/2/object")

    def _execute(self, model: str, method: str, *args: Any, **kwargs: Any) -> Any:
        if self._uid is None or self._models is None:
            self.connect()

        try:
            return self._models.execute_kw(
                self._db, self._uid, self._password, model, method, list(args), kwargs
            )
        except (xmlrpc.client.Fault, OSError) as exc:
            raise OdooConnectionError(f"Odoo call failed ({model}.{method}): {exc}") from exc

    def fetch_contacts(self, offset: int = 0, limit: int = 100, since: str | None = None) -> list[dict]:
        domain = [["write_date", ">=", since]] if since else []
        ids = self._execute(
            "res.partner", "search", domain, offset=offset, limit=limit
        )
        if not ids:
            return []
        return self._execute(
            "res.partner", "read", ids, ["id", "name", "email", "phone", "mobile"]
        )

    def fetch_products(self, offset: int = 0, limit: int = 100, since: str | None = None) -> list[dict]:
        domain = [["write_date", ">=", since]] if since else []
        ids = self._execute(
            "product.product", "search", domain, offset=offset, limit=limit
        )
        if not ids:
            return []
        return self._execute(
            "product.product",
            "read",
            ids,
            ["id", "name", "default_code", "list_price", "type"],
        )

    def fetch_sale_orders(self, offset: int = 0, limit: int = 100, since: str | None = None) -> list[dict]:
        domain = [["write_date", ">=", since]] if since else []
        ids = self._execute(
            "sale.order", "search", domain, offset=offset, limit=limit
        )
        if not ids:
            return []
        return self._execute(
            "sale.order",
            "read",
            ids,
            ["id", "name", "partner_id", "date_order", "state", "amount_total"],
        )

    def fetch_sale_order_lines(self, order_ids: list[int]) -> list[dict]:
        if not order_ids:
            return []
        ids = self._execute(
            "sale.order.line", "search", [["order_id", "in", order_ids]]
        )
        if not ids:
            return []
        return self._execute(
            "sale.order.line",
            "read",
            ids,
            ["id", "order_id", "product_id", "product_uom_qty", "price_unit", "price_subtotal"],
        )