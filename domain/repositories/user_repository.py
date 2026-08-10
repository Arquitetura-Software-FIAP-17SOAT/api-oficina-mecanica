from abc import ABC, abstractmethod

from domain.entities.usuario import Usuario


class UserRepository(ABC):
    """Contrato para persistência de usuários."""

    @abstractmethod
    async def save(self, user: Usuario) -> Usuario:
        pass

    @abstractmethod
    async def find_by_id(self, user_id: int) -> Usuario | None:
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Usuario | None:
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        pass

    @abstractmethod
    async def list(self) -> list[Usuario]:
        pass

    @abstractmethod
    async def update(self, user: Usuario) -> Usuario:
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        pass