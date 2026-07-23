from app.application.dto.product_dto import ProductDTO
from app.domain.entities.product import Product


class ProductMapper:

    @staticmethod
    def to_entity(dto: ProductDTO) -> Product:
        return Product(
            odoo_id=dto.odoo_id,
            name=dto.name,
            internal_reference=dto.internal_reference,
            sale_price=dto.sale_price,
            product_type=dto.product_type,
        )
