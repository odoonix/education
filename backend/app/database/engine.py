from sqlalchemy import create_engine

from app.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)
