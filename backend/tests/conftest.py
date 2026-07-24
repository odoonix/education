"""
Fixture های مشترک pytest.
db_session: یه session روی SQLite In-Memory می‌سازه — برای هر تست تازه و ایزوله.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.base import Base
import models  # noqa: F401  # مطمئن می‌شه همه‌ی مدل‌ها روی Base.metadata ثبت شدن


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)



from database.session import SessionLocal


@pytest.fixture()
def pg_session():
    """
    این fixture به backend-db واقعی وصل می‌شه (نه SQLite).
    برای تست محدودیت‌های واقعی Postgres (Unique, Foreign Key, Cascade) استفاده می‌شه.
    """
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()