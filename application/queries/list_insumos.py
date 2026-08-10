from domain.entities.insumo import Insumo
from domain.repositories.insumo_repository import InsumoRepository


class ListInsumosUseCase:
    """Caso de uso para listagem de insumos."""

    def __init__(self, insumo_repository: InsumoRepository):
        self.insumo_repository = insumo_repository

    async def execute(self) -> list[Insumo]:
        return await self.insumo_repository.list()
