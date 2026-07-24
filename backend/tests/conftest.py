"""
Common fixtures shared across all tests.

The test database URL is read from TEST_DATABASE_URL. With docker compose:
    docker compose --profile test up -d test-db
    TEST_DATABASE_URL=postgresql+psycopg2://app:app@localhost:5434/app_test pytest
Or simpler, through the ready-made tests service in docker-compose (see README).

We have two types of fixtures because we need two different testing patterns:

db_session:
    For tests that work directly with a single Session (Repositories,
    models, SyncRunLogger). Uses SQLAlchemy's official pattern for isolating
    tests with a real database: an outer transaction is opened and the Session
    joins it with join_transaction_mode="create_savepoint" - meaning session.commit()
    inside the test only commits a SAVEPOINT, not the outer transaction.
    At the end of the test, the entire outer transaction is rolled back and the
    database is restored to its previous state. It's fast (no new DDL between tests)
    and completely isolated.

pg_session_factory:
    For Integration tests where the code under test (e.g., SyncOrchestrator)
    creates multiple independent Sessions and actually commits multiple times.
    The savepoint pattern is not suitable for this case because multiple separate
    Sessions cannot share the same connection. Instead, we truncate all tables
    with TRUNCATE ... RESTART IDENTITY CASCADE after each test.

make_fake_odoo_client:
    A factory that creates a fake OdooClient (MagicMock). Simply pass a
    dictionary {model_name: [rows...]} and iter_all()/search_read()
    will return that data - just like the real thing, without needing a real Odoo.
"""
import os
import sys
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.base import Base
from app.db import models

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://app:app@localhost:5434/app_test",
)


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DATABASE_URL, future=True)

    try:
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        pytest.exit(
            "Cannot connect to PostgreSQL test database "
            f"({TEST_DATABASE_URL}).\n"
            "First start the test database:\n"
            "  docker compose --profile test up -d test-db\n"
            "Or run all tests inside Docker:\n"
            "  docker compose --profile test run --rm tests\n"
            f"Original error: {exc}",
            returncode=1,
        )

    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture()
def db_session(engine):
    connection = engine.connect()
    trans = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    trans.rollback()
    connection.close()


@pytest.fixture()
def pg_session_factory(engine):
    factory = sessionmaker(bind=engine, future=True)

    yield factory
    table_names = ", ".join(
        f'"{table.name}"' for table in reversed(Base.metadata.sorted_tables)
    )
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"))


@pytest.fixture()
def make_fake_odoo_client():
    def _factory(data_by_model: dict) -> MagicMock:
        client = MagicMock()

        def _iter_all(model, domain, fields, batch_size=100):  # noqa: ARG001
            return iter(data_by_model.get(model, []))

        def _search_read(model, domain, fields, offset=0, limit=100, order=None):  # noqa: ARG001
            rows = data_by_model.get(model, [])
            return rows[offset : offset + limit]

        client.iter_all.side_effect = _iter_all
        client.search_read.side_effect = _search_read
        return client

    return _factory
