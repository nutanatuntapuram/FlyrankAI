from abc import ABC, abstractmethod
from typing import Optional


class TaskRepository(ABC):
    """
    Defines what any task storage backend must be able to do.
    Routes talk to THIS interface only — never to SQLite, Postgres,
    or any specific database directly.
    """

    @abstractmethod
    def get_all(self) -> list[dict]:
        ...

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[dict]:
        ...

    @abstractmethod
    def create(self, title: str) -> dict:
        ...

    @abstractmethod
    def update(self, task_id: int, title: Optional[str], done: Optional[bool]) -> Optional[dict]:
        ...

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        ...