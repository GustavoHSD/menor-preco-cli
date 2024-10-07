from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

class Repository(Generic[T], ABC):
    @abstractmethod
    def find_by_id(self, id: int) -> T | None:
        pass

    @abstractmethod
    def find_all(self) -> list[T]:
        pass

    @abstractmethod
    def save(self, entity) -> T | None:
        pass

    @abstractmethod
    def delete_by_id(self, id: int):
        pass

