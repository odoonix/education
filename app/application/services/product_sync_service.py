from decimal import Decimal

from app.infrastructure.odoo.client import OdooClient
from app.application.dto.product_dto import ProductDTO
from app.application.mappers.product_mapper import ProductMapper


class ProductSyncService:

    def __init__(
        self,
        odoo_client: OdooClient,
    ):
        self.odoo_client = odoo_client

    def sync(self):

        products = self.odoo_client.get_products()

        entities = []

        for product in products:

            dto = ProductDTO(
                odoo_id=product["id"],
                name=product["name"],
                internal_reference=product.get(
                    "default_code"
                ) or None,
                sale_price=Decimal(
                    str(product["list_price"])
                )
                if product.get("list_price")
                else None,
                product_type=product.get("type"),
            )

            entity = ProductMapper.to_entity(dto)

            entities.append(entity)

        return entities