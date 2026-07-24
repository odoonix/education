import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.infrastructure.db_models import Base

TEST_DB_URL = "postgresql+psycopg2://test_user:test_password@localhost:5434/test_backend"


@pytest.fixture(scope="session")
def engine():
    return create_engine(TEST_DB_URL)


@pytest.fixture(autouse=True)
def _reset_schema(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture
def session(engine) -> Session:
    session_factory = sessionmaker(bind=engine)
    db_session = session_factory()
    yield db_session
    db_session.close()