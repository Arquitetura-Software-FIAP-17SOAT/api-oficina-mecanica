from dataclasses import dataclass

from domain.repositories.veiculo_repository import VeiculoRepository


@dataclass
class DeleteVeiculoCommand:
    veiculo_id: int


class DeleteVeiculoUseCase:
    def __init__(self, veiculo_repository: VeiculoRepository):
        self.veiculo_repository = veiculo_repository

    async def execute(self, command: DeleteVeiculoCommand) -> bool:
        veiculo = await self.veiculo_repository.find_by_id(command.veiculo_id)

        if veiculo is None:
            return False

        if await self.veiculo_repository.has_ordens_servico(command.veiculo_id):
            raise ValueError(
                "O veículo não pode ser excluído porque possui ordens de "
                "serviço registradas."
            )

        await self.veiculo_repository.delete(command.veiculo_id)

        return True
