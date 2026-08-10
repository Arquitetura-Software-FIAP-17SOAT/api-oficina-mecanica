from dataclasses import dataclass

from domain.entities.insumo import Insumo
from domain.repositories.insumo_repository import InsumoRepository


@dataclass
class AddEstoqueCommand:
    """Comando para entrada de estoque."""

    insumo_id: int
    quantidade: int


class AddEstoqueUseCase:
    """Caso de uso para registrar entrada de estoque."""

    def __init__(self, insumo_repository: InsumoRepository):
        self.insumo_repository = insumo_repository

    async def execute(self, command: AddEstoqueCommand) -> Insumo | None:
        insumo = await self.insumo_repository.find_by_id(command.insumo_id)

        if insumo is None:
            return None

        insumo.adicionar_estoque(command.quantidade)

        return await self.insumo_repository.update(insumo)
