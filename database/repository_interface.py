from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from error.EntityNotDeleted import EntityNotDeleted
from error.EntityNotFound import EntityNotFound
from error.EntityNotSaved import EntityNotSaved
from error.Result import Result

T = TypeVar('T')

class Repository(Generic[T], ABC):
    @abstractmethod
    def find_by_id(self, id: int) -> Result[T, EntityNotFound]:
        pass

    @abstractmethod
    def find_all(self) -> list[T]:
        pass

    @abstractmethod
    def save(self, entity) -> Result[T, EntityNotSaved]:
        pass

    @abstractmethod
    def delete_by_id(self, id: int) -> Result[int, EntityNotDeleted]:
        pass

    @abstractmethod
    def exists_by_id(self, id: int) -> bool:
        pass
