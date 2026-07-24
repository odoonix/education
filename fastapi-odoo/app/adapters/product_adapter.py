from app.adapters.odoo_client import OdooClient
from app.schemas.product import (
    OdooProduct,
    OdooProductTemplate,
    OdooProductVariant,
)


class ProductAdapter:
    def __init__(self, client: OdooClient) -> None:
        self._client = client

    def fetch_products(self) -> list[OdooProduct]:
        variants = self._client.search_read(
            model="product.product",
            fields=[
                "id",
                "product_tmpl_id",
                "name",
                "default_code",
                "lst_price",
            ],
        )

        templates = self._client.search_read(
            model="product.template",
            fields=[
                "id",
                "list_price",
                "type",
            ],
        )

        variant_records = [
            OdooProductVariant.model_validate(record)
            for record in variants
        ]

        template_records = [
            OdooProductTemplate.model_validate(record)
            for record in templates
        ]

        templates_by_id = {
            template.odoo_id: template
            for template in template_records
        }

        products: list[OdooProduct] = []

        for variant in variant_records:
            template = templates_by_id.get(
                variant.product_template_id
            )

            if template is None:
                raise ValueError(
                    "Product variant references missing "
                    f"template: {variant.product_template_id}"
                )

            products.append(
                OdooProduct(
                    odoo_id=variant.odoo_id,
                    name=variant.name,
                    internal_reference=(
                        variant.internal_reference
                    ),
                    sale_price=template.sale_price,
                    product_type=template.product_type,
                )
            )

        return products