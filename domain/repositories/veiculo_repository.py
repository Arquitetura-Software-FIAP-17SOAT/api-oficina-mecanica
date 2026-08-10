from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.veiculo import Veiculo


class VeiculoRepository(ABC):
    """Contrato para persistência de veículos."""

    @abstractmethod
    async def save(self, veiculo: Veiculo) -> Veiculo:
        pass

    @abstractmethod
    async def find_by_id(self, veiculo_id: int) -> Veiculo | None:
        pass

    @abstractmethod
    async def list(self, cliente_id: int | None = None) -> list[Veiculo]:
        pass

    @abstractmethod
    async def update(self, veiculo: Veiculo) -> Veiculo:
        pass

    @abstractmethod
    async def delete(self, veiculo_id: int) -> None:
        pass

    @abstractmethod
    async def exists_by_placa(self, placa: str) -> bool:
        pass

    @abstractmethod
    async def marca_exists(self, marca_id: int) -> bool:
        pass

    @abstractmethod
    async def has_ordens_servico(self, veiculo_id: int) -> bool:
        pass
