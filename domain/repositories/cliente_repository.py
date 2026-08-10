from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.cliente import Cliente


class ClienteRepository(ABC):
    """Contrato para persistência de clientes."""

    @abstractmethod
    async def save(self, cliente: Cliente) -> Cliente:
        pass

    @abstractmethod
    async def find_by_id(self, cliente_id: int) -> Cliente | None:
        pass

    @abstractmethod
    async def list(self) -> list[Cliente]:
        pass

    @abstractmethod
    async def update(self, cliente: Cliente) -> Cliente:
        pass

    @abstractmethod
    async def delete(self, cliente_id: int) -> None:
        pass

    @abstractmethod
    async def exists_by_cpf_cnpj(self, cpf_cnpj: str) -> bool:
        pass

    @abstractmethod
    async def has_veiculos(self, cliente_id: int) -> bool:
        pass
