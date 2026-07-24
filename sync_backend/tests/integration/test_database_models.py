from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import sessionmaker

from odoo_sync.config import Settings
from odoo_sync.domain.models import Contact, Product
from odoo_sync.domain.sync import UpsertResult
from odoo_sync.infrastructure.database.models import ContactModel, ProductModel
from odoo_sync.infrastructure.database.repositories import (
    SqlContactRepository,
    SqlProductRepository,
)

pytestmark = pytest.mark.integration


def test_repository_insert_update_unchanged_against_postgresql() -> None:
    settings = Settings()
    engine = create_engine(settings.sync_database_url, pool_pre_ping=True)
    Session = sessionmaker(engine, expire_on_commit=False)
    with Session() as session:
        session.execute(delete(ContactModel).where(ContactModel.odoo_id == 900001))
        contact = Contact(900001, "A", None, None, None, datetime(2026, 7, 24, tzinfo=UTC))
        repo = SqlContactRepository(session)
        assert repo.upsert(contact) is UpsertResult.INSERTED
        session.commit()
        assert repo.upsert(contact) is UpsertResult.UNCHANGED
        assert (
            repo.upsert(Contact(900001, "B", None, None, None, contact.odoo_write_date))
            is UpsertResult.UPDATED
        )
        session.commit()
        assert (
            session.scalar(select(ContactModel.name).where(ContactModel.odoo_id == 900001)) == "B"
        )


def test_product_uses_decimal_against_postgresql() -> None:
    settings = Settings()
    engine = create_engine(settings.sync_database_url, pool_pre_ping=True)
    Session = sessionmaker(engine, expire_on_commit=False)
    with Session() as session:
        session.execute(delete(ProductModel).where(ProductModel.odoo_id == 900001))
        product = Product(900001, "P", "P1", Decimal("12.3400"), "product", None)
        assert SqlProductRepository(session).upsert(product) is UpsertResult.INSERTED
        session.rollback()
