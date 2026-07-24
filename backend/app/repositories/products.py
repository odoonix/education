from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(
    BaseRepository[Product]
):

    def __init__(
        self,
        session: Session,
    ):
        super().__init__(
            session,
            Product,
        )
