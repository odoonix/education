from app.application.dto.sale_order_dto import SaleOrderDTO
from app.domain.entities.sale_order import SaleOrder


class SaleOrderMapper:

    @staticmethod
    def to_entity(dto: SaleOrderDTO) -> SaleOrder:
        return SaleOrder(
            odoo_id=dto.odoo_id,
            order_number=dto.order_number,
            customer_id=dto.customer_id,
            order_date=dto.order_date,
            state=dto.state,
            total_amount=dto.total_amount,
        )
