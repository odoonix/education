from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.odoo_sync import OdooProductData


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_odoo_id(self, odoo_id: int) -> Product | None:
        return self.db.query(Product).filter(Product.odoo_id == odoo_id).first()

    def list(self, skip: int = 0, limit: int = 100) -> list[Product]:
        return (
            self.db.query(Product)
            .order_by(Product.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def upsert(self, data: OdooProductData) -> tuple[Product, bool]:
        product = self.get_by_odoo_id(data.odoo_id)
        created = product is None
        if created:
            product = Product(odoo_id=data.odoo_id)

        product.name = data.name
        product.default_code = data.default_code
        product.list_price = data.list_price
        product.uom_name = data.uom_name
        product.active = data.active

        self.db.add(product)
        self.db.flush()
        return product, created
