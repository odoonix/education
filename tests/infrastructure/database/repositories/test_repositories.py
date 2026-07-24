from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.infrastructure.database.models  # noqa: F401  (register metadata)
from app.infrastructure.database.models.base import Base
from app.infrastructure.database.models.sync_run import SyncRunModel
from app.infrastructure.database.models.sync_log import SyncLogModel
from app.domain.entities.contact import Contact
from app.domain.entities.product import Product
from app.domain.entities.sale_order import SaleOrder
from app.domain.entities.sale_order_line import SaleOrderLine
from app.domain.entities.sync_run import SyncRun, SyncStatus
from app.domain.entities.sync_log import SyncLog, SyncLogLevel
from app.infrastructure.database.repositories.contact_repository import (
    SQLAlchemyContactRepository,
)
from app.infrastructure.database.repositories.product_repository import (
    SQLAlchemyProductRepository,
)
from app.infrastructure.database.repositories.sale_order_repository import (
    SQLAlchemySaleOrderRepository,
)
from app.infrastructure.database.repositories.sale_order_line_repository import (
    SQLAlchemySaleOrderLineRepository,
)
from app.infrastructure.database.repositories.sync_run_repository import (
    SQLAlchemySyncRunRepository,
)


class InMemoryConnection:
    """Test double for IDBConnection backed by shared in-memory SQLite."""

    def __init__(self):
        self._engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self._engine)
        self._session_factory = sessionmaker(bind=self._engine)

    def get_session(self):
        return self._session_factory()

    def get_session_generator(self):
        session = self.get_session()
        try:
            yield session
        finally:
            session.close()

    def dispose(self):
        self._engine.dispose()


@pytest.fixture
def db():
    conn = InMemoryConnection()
    yield conn
    conn.dispose()


def test_contact_repository_save_get_update(db):
    repo = SQLAlchemyContactRepository(db)

    assert repo.get_by_odoo_id(1) is None

    repo.save(Contact(odoo_id=1, name="Ali", email="a@x.com",
                      phone="021", mobile="0912"))
    assert repo.get_by_odoo_id(1) == Contact(
        odoo_id=1, name="Ali", email="a@x.com", phone="021", mobile="0912"
    )

    repo.update(Contact(odoo_id=1, name="Ali Updated", email="new@x.com",
                        phone="022", mobile="0913"))
    updated = repo.get_by_odoo_id(1)
    assert updated.name == "Ali Updated"
    assert updated.email == "new@x.com"


def test_product_repository_save_get_update(db):
    repo = SQLAlchemyProductRepository(db)

    repo.save(Product(odoo_id=1, name="Laptop", internal_reference="LAP-001",
                      sale_price=Decimal("2500.00"), product_type="consu"))
    product = repo.get_by_odoo_id(1)
    assert product.name == "Laptop"
    assert product.sale_price == Decimal("2500.00")

    repo.update(Product(odoo_id=1, name="Laptop v2",
                        internal_reference="LAP-001",
                        sale_price=Decimal("2600.00"), product_type="consu"))
    assert repo.get_by_odoo_id(1).sale_price == Decimal("2600.00")


def test_sale_order_repository_save_get_update(db):
    repo = SQLAlchemySaleOrderRepository(db)
    dt = datetime(2026, 7, 24, 10, 0, 0)

    repo.save(SaleOrder(odoo_id=1, order_number="S00001", customer_id=7,
                        order_date=dt, state="sale",
                        total_amount=Decimal("100.00")))
    order = repo.get_by_odoo_id(1)
    assert order.order_number == "S00001"
    assert order.state == "sale"

    repo.update(SaleOrder(odoo_id=1, order_number="S00001", customer_id=7,
                          order_date=dt, state="done",
                          total_amount=Decimal("100.00")))
    assert repo.get_by_odoo_id(1).state == "done"


def test_sale_order_line_repository_save_get_update(db):
    repo = SQLAlchemySaleOrderLineRepository(db)

    repo.save(SaleOrderLine(odoo_id=1, sale_order_id=10, product_id=20,
                            quantity=2.0, unit_price=Decimal("50.00"),
                            subtotal=Decimal("100.00")))
    line = repo.get_by_odoo_id(1)
    assert line.sale_order_id == 10
    assert line.quantity == 2.0

    repo.update(SaleOrderLine(odoo_id=1, sale_order_id=10, product_id=20,
                              quantity=5.0, unit_price=Decimal("50.00"),
                              subtotal=Decimal("250.00")))
    assert repo.get_by_odoo_id(1).quantity == 5.0


def test_sync_run_repository_lifecycle(db):
    repo = SQLAlchemySyncRunRepository(db)

    run = repo.create(SyncRun(operation_type="contacts",
                              started_at=datetime.now()))
    assert run.id is not None

    repo.add_log(SyncLog(sync_run_id=run.id, level=SyncLogLevel.ERROR,
                         message="boom", odoo_id=42))

    run.records_received = 5
    run.records_saved = 4
    run.records_failed = 1
    run.finished_at = datetime.now()
    run.status = SyncStatus.PARTIAL
    repo.finish(run)

    session = db.get_session()
    model = session.get(SyncRunModel, run.id)
    assert model.status == "partial"
    assert model.records_failed == 1
    assert model.finished_at is not None

    logs = (
        session.query(SyncLogModel)
        .filter_by(sync_run_id=run.id)
        .all()
    )
    assert len(logs) == 1
    assert logs[0].level == "error"
    assert logs[0].odoo_id == 42
    session.close()
