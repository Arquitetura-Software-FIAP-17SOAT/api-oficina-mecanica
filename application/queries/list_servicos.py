from domain.entities.servico import Servico
from domain.repositories.servico_repository import ServicoRepository


class ListServicosUseCase:
    """Caso de uso para listagem de serviços."""

    def __init__(self, servico_repository: ServicoRepository):
        self.servico_repository = servico_repository

    async def execute(self) -> list[Servico]:
        return await self.servico_repository.list()
