from abc import ABC, abstractmethod
from sqlmodel import Session


class CommonRepository(ABC):
    @abstractmethod
    def get_by_id(self, session: Session, id: int):
        pass

    @abstractmethod
    def get_all(self, session: Session):
        pass

    @abstractmethod
    def remove_by_id(self, session: Session, id: int):
        pass

    @abstractmethod
    def update(self, session: Session, id: int, input: object):
        pass

    @abstractmethod
    def create(self, session, input: object):
        pass
