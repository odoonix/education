from datetime import datetime
from decimal import Decimal

from app.application.dto.contact_dto import ContactDTO
from app.application.dto.product_dto import ProductDTO
from app.application.dto.sale_order_dto import SaleOrderDTO
from app.application.dto.sale_order_line_dto import SaleOrderLineDTO
from app.application.mappers.contact_mapper import ContactMapper
from app.application.mappers.product_mapper import ProductMapper
from app.application.mappers.sale_order_mapper import SaleOrderMapper
from app.application.mappers.sale_order_line_mapper import SaleOrderLineMapper
from app.domain.entities.contact import Contact
from app.domain.entities.product import Product
from app.domain.entities.sale_order import SaleOrder
from app.domain.entities.sale_order_line import SaleOrderLine


def test_contact_mapper_to_entity():
    dto = ContactDTO(odoo_id=1, name="Ali", email="a@x.com",
                     phone="021", mobile="0912")
    entity = ContactMapper.to_entity(dto)

    assert isinstance(entity, Contact)
    assert entity.odoo_id == 1
    assert entity.name == "Ali"
    assert entity.email == "a@x.com"
    assert entity.phone == "021"
    assert entity.mobile == "0912"


def test_product_mapper_to_entity():
    dto = ProductDTO(odoo_id=2, name="Laptop", internal_reference="LAP-001",
                     sale_price=Decimal("2500.00"), product_type="consu")
    entity = ProductMapper.to_entity(dto)

    assert isinstance(entity, Product)
    assert entity.odoo_id == 2
    assert entity.internal_reference == "LAP-001"
    assert entity.sale_price == Decimal("2500.00")
    assert entity.product_type == "consu"


def test_sale_order_mapper_to_entity():
    dt = datetime(2026, 7, 24, 10, 0, 0)
    dto = SaleOrderDTO(odoo_id=3, order_number="S00001", customer_id=7,
                       order_date=dt, state="sale",
                       total_amount=Decimal("100.00"))
    entity = SaleOrderMapper.to_entity(dto)

    assert isinstance(entity, SaleOrder)
    assert entity.order_number == "S00001"
    assert entity.customer_id == 7
    assert entity.order_date == dt
    assert entity.state == "sale"
    assert entity.total_amount == Decimal("100.00")


def test_sale_order_line_mapper_to_entity():
    dto = SaleOrderLineDTO(odoo_id=4, sale_order_id=3, product_id=2,
                           quantity=2.0, unit_price=Decimal("50.00"),
                           subtotal=Decimal("100.00"))
    entity = SaleOrderLineMapper.to_entity(dto)

    assert isinstance(entity, SaleOrderLine)
    assert entity.sale_order_id == 3
    assert entity.product_id == 2
    assert entity.quantity == 2.0
    assert entity.unit_price == Decimal("50.00")
    assert entity.subtotal == Decimal("100.00")
