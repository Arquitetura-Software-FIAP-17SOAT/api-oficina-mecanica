from domain.entities.veiculo import Veiculo
from domain.repositories.veiculo_repository import VeiculoRepository


class ListVeiculosUseCase:
    """Caso de uso para listagem de veículos, opcionalmente por cliente."""

    def __init__(self, veiculo_repository: VeiculoRepository):
        self.veiculo_repository = veiculo_repository

    async def execute(self, cliente_id: int | None = None) -> list[Veiculo]:
        return await self.veiculo_repository.list(cliente_id=cliente_id)
