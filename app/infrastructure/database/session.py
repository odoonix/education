from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from typing import Generator

from app.config.settings import settings
from app.domain.ports.db_session import IDBConnection


class PostgreSQLConnection(IDBConnection):

    def __init__(self):
        database_url = str(settings.POSTGRES_DATABASE_URL).replace(
            "postgresql://", "postgresql+psycopg://", 1
        )
        self._engine: Engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        self._session_factory: sessionmaker = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False
        )

    def get_session(self) -> Session:
        return self._session_factory()
    
    def get_session_generator(self) -> Generator[Session, None, None]:
        session = self.get_session()
        try:
            yield session
        finally:
            session.close()

    def dispose(self) -> None:
        self._engine.dispose()
        