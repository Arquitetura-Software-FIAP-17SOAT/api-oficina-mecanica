from domain.entities.servico import Servico
from domain.repositories.servico_repository import ServicoRepository


class GetServicoUseCase:
    """Caso de uso para consulta de um serviço pelo id."""

    def __init__(self, servico_repository: ServicoRepository):
        self.servico_repository = servico_repository

    async def execute(self, servico_id: int) -> Servico | None:
        return await self.servico_repository.find_by_id(servico_id)
