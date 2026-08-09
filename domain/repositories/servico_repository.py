from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.servico import Servico


class ServicoRepository(ABC):
    """Contrato para persistência de serviços."""

    @abstractmethod
    async def save(self, servico: Servico) -> Servico:
        pass

    @abstractmethod
    async def find_by_id(self, servico_id: int) -> Servico | None:
        pass

    @abstractmethod
    async def list(self) -> list[Servico]:
        pass

    @abstractmethod
    async def update(self, servico: Servico) -> Servico:
        pass

    @abstractmethod
    async def delete(self, servico_id: int) -> None:
        pass

    @abstractmethod
    async def exists_by_nome(self, nome: str) -> bool:
        pass

    @abstractmethod
    async def has_vinculos(self, servico_id: int) -> bool:
        pass
