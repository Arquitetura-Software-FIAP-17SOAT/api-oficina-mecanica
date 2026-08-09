from domain.entities.veiculo import Veiculo
from domain.repositories.veiculo_repository import VeiculoRepository


class GetVeiculoUseCase:
    """Caso de uso para consulta de um veículo pelo id."""

    def __init__(self, veiculo_repository: VeiculoRepository):
        self.veiculo_repository = veiculo_repository

    async def execute(self, veiculo_id: int) -> Veiculo | None:
        return await self.veiculo_repository.find_by_id(veiculo_id)
