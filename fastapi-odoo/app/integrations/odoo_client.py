from xmlrpc import client as xmlrpc_client

from app.core.config import settings
from app.schemas.odoo import OdooHealth, OdooPartnerCreate, OdooPartnerRead
from app.schemas.odoo_sync import (
    OdooContactData,
    OdooProductData,
    OdooSaleOrderData,
    OdooSaleOrderLineData,
)


class OdooClientError(Exception):
    """Raised when an Odoo XML-RPC call fails."""


CONTACT_FIELDS = [
    "id",
    "name",
    "email",
    "phone",
    "street",
    "city",
    "country_id",
    "is_company",
]

PRODUCT_FIELDS = [
    "id",
    "name",
    "default_code",
    "list_price",
    "uom_id",
    "active",
]

SALE_ORDER_FIELDS = [
    "id",
    "name",
    "partner_id",
    "state",
    "amount_total",
    "date_order",
    "order_line",
]

SALE_ORDER_LINE_FIELDS = [
    "id",
    "order_id",
    "product_id",
    "name",
    "product_uom_qty",
    "price_unit",
    "price_subtotal",
]


class OdooClient:
    """Thin XML-RPC client for communicating with the Odoo server."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        db: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        self.host = host or settings.ODOO_HOST
        self.port = port or settings.ODOO_PORT
        self.db = db or settings.ODOO_DB
        self.user = user or settings.ODOO_USER
        self.password = password or settings.ODOO_PASSWORD
        self._uid: int | None = None

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def _common(self) -> xmlrpc_client.ServerProxy:
        return xmlrpc_client.ServerProxy(f"{self.base_url}/xmlrpc/2/common", allow_none=True)

    def _object(self) -> xmlrpc_client.ServerProxy:
        return xmlrpc_client.ServerProxy(f"{self.base_url}/xmlrpc/2/object", allow_none=True)

    def authenticate(self) -> int:
        try:
            uid = self._common().authenticate(self.db, self.user, self.password, {})
        except Exception as exc:  # noqa: BLE001
            raise OdooClientError(f"Odoo authentication failed: {exc}") from exc
        if not uid:
            raise OdooClientError(
                "Odoo authentication returned no uid. "
                "Create the Odoo database and admin user first (http://localhost:8069)."
            )
        self._uid = int(uid)
        return self._uid

    @property
    def uid(self) -> int:
        if self._uid is None:
            return self.authenticate()
        return self._uid

    def execute_kw(
        self,
        model: str,
        method: str,
        args: list | None = None,
        kwargs: dict | None = None,
    ):
        try:
            return self._object().execute_kw(
                self.db,
                self.uid,
                self.password,
                model,
                method,
                args or [],
                kwargs or {},
            )
        except OdooClientError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise OdooClientError(f"Odoo call {model}.{method} failed: {exc}") from exc

    def search_read(
        self,
        model: str,
        domain: list | None = None,
        fields: list[str] | None = None,
        limit: int | None = None,
        order: str | None = None,
    ) -> list[dict]:
        kwargs: dict = {}
        if fields:
            kwargs["fields"] = fields
        if limit is not None:
            kwargs["limit"] = limit
        if order:
            kwargs["order"] = order
        return self.execute_kw(model, "search_read", [domain or []], kwargs)

    def health(self) -> OdooHealth:
        try:
            version = self._common().version()
            uid = self.authenticate()
            return OdooHealth(
                connected=True,
                version=version.get("server_version") if isinstance(version, dict) else str(version),
                uid=uid,
            )
        except Exception as exc:  # noqa: BLE001
            return OdooHealth(connected=False, detail=str(exc))

    def fetch_contacts(self, limit: int | None = None) -> list[OdooContactData]:
        records = self.search_read(
            "res.partner",
            domain=[("customer_rank", ">", 0)],
            fields=CONTACT_FIELDS,
            limit=limit,
            order="id asc",
        )
        return [OdooContactData.from_odoo(r) for r in records]

    def fetch_products(self, limit: int | None = None) -> list[OdooProductData]:
        records = self.search_read(
            "product.product",
            domain=[("sale_ok", "=", True)],
            fields=PRODUCT_FIELDS,
            limit=limit,
            order="id asc",
        )
        return [OdooProductData.from_odoo(r) for r in records]

    def fetch_product_by_id(self, product_id: int) -> OdooProductData | None:
        records = self.execute_kw(
            "product.product",
            "read",
            [[product_id]],
            {"fields": PRODUCT_FIELDS},
        )
        if not records:
            return None
        return OdooProductData.from_odoo(records[0])

    def fetch_sale_orders(self, limit: int | None = None) -> list[OdooSaleOrderData]:
        records = self.search_read(
            "sale.order",
            domain=[],
            fields=SALE_ORDER_FIELDS,
            limit=limit,
            order="id asc",
        )
        return [OdooSaleOrderData.from_odoo(r) for r in records]

    def fetch_sale_order_lines(self, line_ids: list[int]) -> list[OdooSaleOrderLineData]:
        if not line_ids:
            return []
        records = self.execute_kw(
            "sale.order.line",
            "read",
            [line_ids],
            {"fields": SALE_ORDER_LINE_FIELDS},
        )
        return [OdooSaleOrderLineData.from_odoo(r) for r in records]

    def fetch_contact_by_id(self, partner_id: int) -> OdooContactData | None:
        records = self.execute_kw(
            "res.partner",
            "read",
            [[partner_id]],
            {"fields": CONTACT_FIELDS},
        )
        if not records:
            return None
        return OdooContactData.from_odoo(records[0])

    def create_partner(self, payload: OdooPartnerCreate) -> OdooPartnerRead:
        values = {"name": payload.name, "customer_rank": 1}
        if payload.email:
            values["email"] = payload.email
        if payload.phone:
            values["phone"] = payload.phone

        partner_id = self.execute_kw("res.partner", "create", [values])
        records = self.execute_kw(
            "res.partner",
            "read",
            [[partner_id]],
            {"fields": ["id", "name", "email", "phone"]},
        )
        record = records[0]
        return OdooPartnerRead(
            id=record["id"],
            name=record["name"],
            email=record.get("email") or None,
            phone=record.get("phone") or None,
        )

    def list_partners(self, limit: int = 20) -> list[OdooPartnerRead]:
        ids = self.execute_kw(
            "res.partner",
            "search",
            [[("customer_rank", ">", 0)]],
            {"limit": limit, "order": "id desc"},
        )
        if not ids:
            return []
        records = self.execute_kw(
            "res.partner",
            "read",
            [ids],
            {"fields": ["id", "name", "email", "phone"]},
        )
        return [
            OdooPartnerRead(
                id=r["id"],
                name=r["name"],
                email=r.get("email") or None,
                phone=r.get("phone") or None,
            )
            for r in records
        ]

    def _create_sale_product(self, name: str, code: str, price: float) -> int:
        template_id = self.execute_kw(
            "product.template",
            "create",
            [{
                "name": name,
                "default_code": code,
                "list_price": price,
                "type": "service",
                "sale_ok": True,
            }],
        )
        variants = self.search_read(
            "product.product",
            domain=[("product_tmpl_id", "=", template_id)],
            fields=["id"],
            limit=1,
        )
        return variants[0]["id"]

    def seed_demo_data(self) -> dict[str, int | list[int]]:
        """Create sample contacts, products, and sale orders in Odoo."""
        partner_a = self.execute_kw(
            "res.partner",
            "create",
            [{
                "name": "Acme Corp",
                "email": "contact@acme.example",
                "phone": "+1-555-0100",
                "street": "123 Main St",
                "city": "New York",
                "customer_rank": 1,
                "is_company": True,
            }],
        )
        partner_b = self.execute_kw(
            "res.partner",
            "create",
            [{
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "+1-555-0200",
                "customer_rank": 1,
            }],
        )

        product_a = self._create_sale_product("Consulting Hours", "CONS-001", 150.0)
        product_b = self._create_sale_product("Software License", "LIC-001", 999.0)

        order_id = self.execute_kw(
            "sale.order",
            "create",
            [{
                "partner_id": partner_a,
                "order_line": [
                    (0, 0, {"product_id": product_a, "product_uom_qty": 10}),
                    (0, 0, {"product_id": product_b, "product_uom_qty": 2}),
                ],
            }],
        )

        order_b_id = self.execute_kw(
            "sale.order",
            "create",
            [{
                "partner_id": partner_b,
                "order_line": [
                    (0, 0, {"product_id": product_a, "product_uom_qty": 5}),
                ],
            }],
        )

        return {
            "partners": [partner_a, partner_b],
            "products": [product_a, product_b],
            "sale_orders": [order_id, order_b_id],
        }


def get_odoo_client() -> OdooClient:
    return OdooClient()
