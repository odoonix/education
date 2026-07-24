from sqlalchemy.orm import Session

from app.models.sale_order import SaleOrder
from app.repositories.base import BaseRepository


class SaleOrderRepository(
    BaseRepository[SaleOrder]
):

    def __init__(
        self,
        session: Session,
    ):
        super().__init__(
            session,
            SaleOrder,
        )
