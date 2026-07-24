import xmlrpc.client

from app.infrastructure.odoo.constants import (
    ODOO_COMMON_ENDPOINT,
    ODOO_OBJECT_ENDPOINT,
)

from app.infrastructure.odoo.exceptions import (
    OdooAuthenticationError,
    OdooConnectionError,
)

class OdooClient:

    def __init__(
        self,
        url: str,
        database: str,
        username: str,
        password: str,
    ):
        self.url = url
        self.database = database
        self.username = username
        self.password = password

        self.uid = None

        self.common = xmlrpc.client.ServerProxy(
            f"{url}{ODOO_COMMON_ENDPOINT}"
        )

        self.models = xmlrpc.client.ServerProxy(
            f"{url}{ODOO_OBJECT_ENDPOINT}"
        )


    def authenticate(self) -> int:
        try:
            uid = self.common.authenticate(
                self.database,
                self.username,
                self.password,
                {},
            )

        except Exception as exc:
            raise OdooConnectionError(str(exc))


        if not uid:
            raise OdooAuthenticationError(
                "Invalid Odoo credentials"
            )

        self.uid = uid

        return uid
    
    def get_contacts(self):
        if not self.uid:
            raise OdooAuthenticationError(
                "Authenticate first"
            )

        contacts = self.models.execute_kw(
            self.database,
            self.uid,
            self.password,
            "res.partner",
            "search_read",
            [],
            {
                "fields": [
                    "id",
                    "name",
                    "email",
                    "phone",
                    "mobile",
                ]
            },
        )

        return contacts
    
    def get_products(self):

        if not self.uid:
            raise OdooAuthenticationError(
                "Authenticate first"
            )

        products = self.models.execute_kw(
            self.database,
            self.uid,
            self.password,
            "product.product",
            "search_read",
            [],
            {
                "fields": [
                    "id",
                    "name",
                    "default_code",
                    "list_price",
                    "type",
                ]
            },
        )

        return products

    def get_sale_orders(self):

        if not self.uid:
            raise OdooAuthenticationError(
                "Authenticate first"
            )

        sale_orders = self.models.execute_kw(
            self.database,
            self.uid,
            self.password,
            "sale.order",
            "search_read",
            [],
            {
                "fields": [
                    "id",
                    "name",
                    "partner_id",
                    "date_order",
                    "state",
                    "amount_total",
                ]
            },
        )

        return sale_orders

    def get_sale_order_lines(self):

        if not self.uid:
            raise OdooAuthenticationError(
                "Authenticate first"
            )

        sale_order_lines = self.models.execute_kw(
            self.database,
            self.uid,
            self.password,
            "sale.order.line",
            "search_read",
            [],
            {
                "fields": [
                    "id",
                    "order_id",
                    "product_id",
                    "product_uom_qty",
                    "price_unit",
                    "price_subtotal",
                ]
            },
        )

        return sale_order_lines