from abc import ABC, abstractmethod
from typing import Generator
from sqlalchemy.orm import Session


class IDBConnection(ABC):

    @abstractmethod
    def get_session(self) -> Session:
        pass

    @abstractmethod
    def get_session_generator(self) -> Generator[Session, None, None]:
        pass

    @abstractmethod
    def dispose(self) -> None:
        pass
    