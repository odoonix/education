
import socket
import xmlrpc.client

from core.interfaces import ERPAdapterInterface
from core.exceptions import OdooAuthenticationError
from core.retry import retry


TRANSIENT_EXCEPTIONS = (
    socket.timeout,
    TimeoutError,
    ConnectionRefusedError,
    ConnectionResetError,
    OSError,
)

class OdooAdapter(ERPAdapterInterface):
    def __init__(self, url: str, db: str, username: str, password: str):
        self._url = url
        self._db = db
        self._username = username
        self._password = password
        self._uid: int | None = None
        self._models = None

    def _connect(self) -> None:

        if self._uid is not None:
            return

        common = xmlrpc.client.ServerProxy(f"{self._url}/xmlrpc/2/common")
        uid = common.authenticate(self._db, self._username, self._password, {})
        if not uid:
            raise OdooAuthenticationError("Odoo authentication failed. Check credentials.")

        self._uid = uid
        self._models = xmlrpc.client.ServerProxy(f"{self._url}/xmlrpc/2/object")



    @retry(max_attempts=3, base_delay=1.0, exceptions=TRANSIENT_EXCEPTIONS)
    def _call(self, model: str, method: str, *args, **kwargs):
        self._connect()
        return self._models.execute_kw(
            self._db, self._uid, self._password, model, method, list(args), kwargs
        )

    def get_contacts(self, offset: int = 0, limit: int = 1000) -> list[dict]:
        return self._call(
            "res.partner", "search_read", [],
            fields=["id", "name", "email", "phone", "mobile"],
            offset=offset, limit=limit,
        )

    def count_contacts(self) -> int:
        return self._call("res.partner", "search_count", [])

    def get_products(self, offset: int = 0, limit: int = 1000) -> list[dict]:
        return self._call(
            "product.template", "search_read", [],
            fields=["id", "name", "default_code", "list_price", "type"],
            offset=offset, limit=limit,
        )

    def count_products(self) -> int:
        return self._call("product.template", "search_count", [])

    def get_sale_orders(self, offset: int = 0, limit: int = 1000) -> list[dict]:
        return self._call(
            "sale.order", "search_read", [],
            fields=["id", "name", "partner_id", "date_order", "state", "amount_total"],
            offset=offset, limit=limit,
        )

    def count_sale_orders(self) -> int:
        return self._call("sale.order", "search_count", [])

    def get_sale_order_lines(self, offset: int = 0, limit: int = 1000) -> list[dict]:
        return self._call(
            "sale.order.line", "search_read", [],
            fields=["id", "order_id", "product_id", "product_uom_qty", "price_unit", "price_subtotal"],
            offset=offset, limit=limit,
        )

    def count_sale_order_lines(self) -> int:
        return self._call("sale.order.line", "search_count", [])