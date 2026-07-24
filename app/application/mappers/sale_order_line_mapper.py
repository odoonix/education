from app.application.dto.sale_order_line_dto import SaleOrderLineDTO
from app.domain.entities.sale_order_line import SaleOrderLine


class SaleOrderLineMapper:

    @staticmethod
    def to_entity(dto: SaleOrderLineDTO) -> SaleOrderLine:
        return SaleOrderLine(
            odoo_id=dto.odoo_id,
            sale_order_id=dto.sale_order_id,
            product_id=dto.product_id,
            quantity=dto.quantity,
            unit_price=dto.unit_price,
            subtotal=dto.subtotal,
        )
