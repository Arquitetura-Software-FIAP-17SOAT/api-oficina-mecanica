from domain.entities.cliente import Cliente
from domain.repositories.cliente_repository import ClienteRepository


class GetClienteUseCase:
    """Caso de uso para consulta de um cliente pelo id."""

    def __init__(self, cliente_repository: ClienteRepository):
        self.cliente_repository = cliente_repository

    async def execute(self, cliente_id: int) -> Cliente | None:
        return await self.cliente_repository.find_by_id(cliente_id)
