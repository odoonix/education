from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import OdooProduct


class ProductRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_odoo_id(
        self,
        odoo_id: int,
    ) -> Product | None:
        statement = select(Product).where(
            Product.odoo_id == odoo_id,
        )

        return self._session.scalar(statement)

    def create(
        self,
        product_data: OdooProduct,
    ) -> Product:
        product = Product(
            odoo_id=product_data.odoo_id,
            name=product_data.name,
            internal_reference=(
                product_data.internal_reference
            ),
            sale_price=product_data.sale_price,
            product_type=product_data.product_type,
        )

        self._session.add(product)

        return product

    def update(
        self,
        product: Product,
        product_data: OdooProduct,
    ) -> Product:
        product.name = product_data.name
        product.internal_reference = (
            product_data.internal_reference
        )
        product.sale_price = product_data.sale_price
        product.product_type = product_data.product_type

        return product