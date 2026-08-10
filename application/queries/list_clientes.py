from domain.entities.cliente import Cliente
from domain.repositories.cliente_repository import ClienteRepository


class ListClientesUseCase:
    """Caso de uso para listagem de clientes."""

    def __init__(self, cliente_repository: ClienteRepository):
        self.cliente_repository = cliente_repository

    async def execute(self) -> list[Cliente]:
        return await self.cliente_repository.list()
