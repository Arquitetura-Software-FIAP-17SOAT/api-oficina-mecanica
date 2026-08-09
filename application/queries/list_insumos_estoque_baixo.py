from domain.entities.insumo import Insumo
from domain.repositories.insumo_repository import InsumoRepository


class ListInsumosEstoqueBaixoUseCase:
    """Caso de uso para listar insumos que precisam de reposição."""

    def __init__(self, insumo_repository: InsumoRepository):
        self.insumo_repository = insumo_repository

    async def execute(self) -> list[Insumo]:
        return await self.insumo_repository.list_estoque_baixo()
