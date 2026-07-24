from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from odoo_sync.config import Settings


def make_session_factory(settings: Settings) -> sessionmaker[Session]:
    engine = create_engine(settings.sync_database_url, pool_pre_ping=True)
    return sessionmaker(engine, expire_on_commit=False)
