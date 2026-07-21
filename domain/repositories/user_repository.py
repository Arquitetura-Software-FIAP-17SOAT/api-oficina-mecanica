from abc import ABC, abstractmethod

from domain.entities.user import User


class UserRepository(ABC):
    """Contrato para persistência de usuários."""

    @abstractmethod
    async def save(self, user: User) -> User:
        pass

    @abstractmethod
    async def find_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        pass

    @abstractmethod
    async def list(self) -> list[User]:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        pass