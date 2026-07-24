from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from odoo_sync.config import Settings


def make_engine(settings: Settings) -> Engine:
    return create_engine(
        settings.sync_database_url,
        pool_pre_ping=True,
    )


def make_session_factory(
    engine: Engine,
) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )
