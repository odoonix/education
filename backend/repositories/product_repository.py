from sqlalchemy.orm import Session

from core.entities import ProductEntity
from core.interfaces import ProductRepositoryInterface
from models.product import Product


class ProductRepository(ProductRepositoryInterface):
    def __init__(self, session: Session):
        self._session = session

    def get_by_odoo_id(self, odoo_id: int) -> Product | None:
        return self._session.query(Product).filter_by(odoo_id=odoo_id).first()

    def upsert(self, entity: ProductEntity) -> tuple[int, bool]:
        existing = self.get_by_odoo_id(entity.odoo_id)

        if existing:
            existing.name = entity.name
            existing.default_code = entity.default_code
            existing.list_price = entity.list_price
            existing.product_type = entity.product_type
            self._session.flush()
            return existing.id, False

        new_product = Product(
            odoo_id=entity.odoo_id,
            name=entity.name,
            default_code=entity.default_code,
            list_price=entity.list_price,
            product_type=entity.product_type,
        )
        self._session.add(new_product)
        self._session.flush()
        return new_product.id, True