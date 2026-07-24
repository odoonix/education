from typing import Callable

from sqlalchemy.orm import Session

from app.domain.entities.product import Product
from app.domain.repositories.product_repository import ProductRepository
from app.infrastructure.database.models.product import ProductModel


class SQLAlchemyProductRepository(ProductRepository):

    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory

    def save(self, product: Product) -> None:
        session = self._session_factory()
        try:
            session.add(self._to_model(product))
            session.commit()
        finally:
            session.close()

    def get_by_odoo_id(self, odoo_id: int) -> Product | None:
        session = self._session_factory()
        try:
            model = session.get(ProductModel, odoo_id)
            return self._to_entity(model) if model else None
        finally:
            session.close()

    def update(self, product: Product) -> None:
        session = self._session_factory()
        try:
            model = session.get(ProductModel, product.odoo_id)
            if model is None:
                return
            model.name = product.name
            model.internal_reference = product.internal_reference
            model.sale_price = product.sale_price
            model.product_type = product.product_type
            session.commit()
        finally:
            session.close()

    @staticmethod
    def _to_model(product: Product) -> ProductModel:
        return ProductModel(
            odoo_id=product.odoo_id,
            name=product.name,
            internal_reference=product.internal_reference,
            sale_price=product.sale_price,
            product_type=product.product_type,
        )

    @staticmethod
    def _to_entity(model: ProductModel) -> Product:
        return Product(
            odoo_id=model.odoo_id,
            name=model.name,
            internal_reference=model.internal_reference,
            sale_price=model.sale_price,
            product_type=model.product_type,
        )
