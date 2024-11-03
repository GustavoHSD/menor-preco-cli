from typing import Generic, Optional, TypeVar

T = TypeVar("T")
E = TypeVar("E", bound=Exception)

class Result(Generic[T, E]):
    def __init__(self, value: Optional[T], error: Optional[E]) -> None:
        self.value = value
        self.error = error
    
    def __str__(self) -> str:
        return f"Result(value={self.value}, error={self.error})"
