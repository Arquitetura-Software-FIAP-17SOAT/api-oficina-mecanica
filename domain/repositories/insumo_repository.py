from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.insumo import Insumo


class InsumoRepository(ABC):
    """Contrato para persistência de insumos."""

    @abstractmethod
    async def save(self, insumo: Insumo) -> Insumo:
        pass

    @abstractmethod
    async def find_by_id(self, insumo_id: int) -> Insumo | None:
        pass

    @abstractmethod
    async def list(self) -> list[Insumo]:
        pass

    @abstractmethod
    async def list_estoque_baixo(self) -> list[Insumo]:
        pass

    @abstractmethod
    async def update(self, insumo: Insumo) -> Insumo:
        pass

    @abstractmethod
    async def delete(self, insumo_id: int) -> None:
        pass

    @abstractmethod
    async def exists_by_nome(self, nome: str) -> bool:
        pass

    @abstractmethod
    async def has_vinculos(self, insumo_id: int) -> bool:
        pass

    @abstractmethod
    async def list_by_servico_id(self, servico_id: int) -> list[Insumo]:
        """Lista os insumos (peças/materiais) que compõem um serviço."""
        pass
