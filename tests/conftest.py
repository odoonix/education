"""
conftest.py فایل مخصوص pytest هست که fixtureهای مشترک بین همه‌ی تست‌ها رو
تعریف می‌کنه، بدون اینکه لازم باشه هر فایل تست جدا importشون کنه.

از SQLite در حافظه (نه فایل واقعی، نه Postgres واقعی) استفاده می‌کنیم تا:
- تست‌ها خیلی سریع اجرا بشن
- نیازی به Docker/app-db روشن نباشه برای اجرای تست‌ها
- هر تست از صفر (دیتابیس خالی) شروع بشه، بدون تداخل با تست‌های دیگه
"""

import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.db.models import Base


@pytest.fixture
def session():
    """یک Session تازه با دیتابیس SQLite خالی در حافظه، برای هر تست جداگانه."""
    engine = create_engine("sqlite:///:memory:")

    # این دو event listener لازمن که SQLite بتونه SAVEPOINT
    # (یعنی session.begin_nested() که تو BaseSyncService استفاده کردیم)
    # رو درست پشتیبانی کنه. بدون این‌ها، pysqlite رفتار Transaction عجیبی
    # داره و تست‌های Error Handling درست کار نمی‌کنن. (این یه محدودیت
    # شناخته‌شده‌ی خود درایور pysqlite هست، نه SQLAlchemy یا کد ما.)
    @event.listens_for(engine, "connect")
    def _set_sqlite_isolation(dbapi_connection, connection_record):
        dbapi_connection.isolation_level = None

    @event.listens_for(engine, "begin")
    def _emit_begin(conn):
        conn.exec_driver_sql("BEGIN")

    Base.metadata.create_all(engine)
    session_local = sessionmaker(bind=engine)
    db_session = session_local()
    yield db_session
    db_session.close()
