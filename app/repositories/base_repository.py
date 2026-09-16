from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from app.utils.database import Database

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Полиморфный CRUD-контракт для всех репозиториев предметной области."""

    def __init__(self, database: Database) -> None:
        self._database = database

    @abstractmethod
    def create(self, entity: T) -> T: ...

    @abstractmethod
    def get_all(self) -> list[T]: ...

    @abstractmethod
    def get_by_id(self, entity_id: int) -> T | None: ...

    @abstractmethod
    def update(self, entity: T) -> T: ...

    @abstractmethod
    def delete(self, entity_id: int) -> bool: ...
