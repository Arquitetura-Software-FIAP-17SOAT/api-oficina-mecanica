from domain.entities.insumo import Insumo
from domain.repositories.insumo_repository import InsumoRepository


class GetInsumoUseCase:
    """Caso de uso para consulta de um insumo pelo id."""

    def __init__(self, insumo_repository: InsumoRepository):
        self.insumo_repository = insumo_repository

    async def execute(self, insumo_id: int) -> Insumo | None:
        return await self.insumo_repository.find_by_id(insumo_id)
