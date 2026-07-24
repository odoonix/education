from sqlalchemy.orm import Session

from backend.domain.entities import Contact, Product, SaleOrder, SaleOrderLine
from backend.infrastructure.db_models import (
    ContactModel,
    ProductModel,
    SaleOrderLineModel,
    SaleOrderModel,
)


class ContactRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert(self, contact: Contact) -> tuple[ContactModel, bool]:
        existing = (
            self._session.query(ContactModel)
            .filter_by(odoo_id=contact.odoo_id)
            .one_or_none()
        )

        if existing is None:
            model = ContactModel(
                odoo_id=contact.odoo_id,
                name=contact.name,
                email=contact.email,
                phone=contact.phone,
                mobile=contact.mobile,
            )
            self._session.add(model)
            self._session.flush()
            return model, True

        existing.name = contact.name
        existing.email = contact.email
        existing.phone = contact.phone
        existing.mobile = contact.mobile
        self._session.flush()
        return existing, False

    def get_by_odoo_id(self, odoo_id: int) -> ContactModel | None:
        return self._session.query(ContactModel).filter_by(odoo_id=odoo_id).one_or_none()


class ProductRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert(self, product: Product) -> tuple[ProductModel, bool]:
        existing = (
            self._session.query(ProductModel)
            .filter_by(odoo_id=product.odoo_id)
            .one_or_none()
        )

        if existing is None:
            model = ProductModel(
                odoo_id=product.odoo_id,
                name=product.name,
                internal_reference=product.internal_reference,
                sale_price=product.sale_price,
                product_type=product.product_type,
            )
            self._session.add(model)
            self._session.flush()
            return model, True

        existing.name = product.name
        existing.internal_reference = product.internal_reference
        existing.sale_price = product.sale_price
        existing.product_type = product.product_type
        self._session.flush()
        return existing, False

    def get_by_odoo_id(self, odoo_id: int) -> ProductModel | None:
        return self._session.query(ProductModel).filter_by(odoo_id=odoo_id).one_or_none()


class SaleOrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert(
        self, order: SaleOrder, customer: ContactModel, product_lookup: dict[int, ProductModel]
    ) -> tuple[SaleOrderModel, bool]:
        existing = (
            self._session.query(SaleOrderModel)
            .filter_by(odoo_id=order.odoo_id)
            .one_or_none()
        )

        if existing is None:
            model = SaleOrderModel(
                odoo_id=order.odoo_id,
                order_number=order.order_number,
                customer=customer,
                order_date=order.order_date,
                state=order.state,
                total_amount=order.total_amount,
            )
            self._session.add(model)
            self._session.flush()
            is_new = True
        else:
            existing.order_number = order.order_number
            existing.customer = customer
            existing.order_date = order.order_date
            existing.state = order.state
            existing.total_amount = order.total_amount
            model = existing
            is_new = False

        self._upsert_lines(model, order.lines, product_lookup)
        self._session.flush()
        return model, is_new

    def _upsert_lines(
        self,
        order_model: SaleOrderModel,
        lines: list[SaleOrderLine],
        product_lookup: dict[int, ProductModel],
    ) -> None:
        existing_by_odoo_id = {line.odoo_id: line for line in order_model.lines}

        for line in lines:
            product = product_lookup[line.product_odoo_id]
            existing_line = existing_by_odoo_id.get(line.odoo_id)

            if existing_line is None:
                new_line = SaleOrderLineModel(
                    odoo_id=line.odoo_id,
                    product=product,
                    quantity=line.quantity,
                    unit_price=line.unit_price,
                    subtotal=line.subtotal,
                )
                order_model.lines.append(new_line)
            else:
                existing_line.product = product
                existing_line.quantity = line.quantity
                existing_line.unit_price = line.unit_price
                existing_line.subtotal = line.subtotal

    def get_by_odoo_id(self, odoo_id: int) -> SaleOrderModel | None:
        return self._session.query(SaleOrderModel).filter_by(odoo_id=odoo_id).one_or_none()