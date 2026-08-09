from dataclasses import dataclass

from domain.entities.insumo import Insumo
from domain.repositories.insumo_repository import InsumoRepository


@dataclass
class RemoveEstoqueCommand:
    """Comando para saída de estoque."""

    insumo_id: int
    quantidade: int


class RemoveEstoqueUseCase:
    """Caso de uso para registrar saída de estoque."""

    def __init__(self, insumo_repository: InsumoRepository):
        self.insumo_repository = insumo_repository

    async def execute(self, command: RemoveEstoqueCommand) -> Insumo | None:
        insumo = await self.insumo_repository.find_by_id(command.insumo_id)

        if insumo is None:
            return None

        insumo.remover_estoque(command.quantidade)

        return await self.insumo_repository.update(insumo)
