from dataclasses import dataclass

from domain.repositories.servico_repository import ServicoRepository


@dataclass
class DeleteServicoCommand:
    servico_id: int


class DeleteServicoUseCase:
    def __init__(self, servico_repository: ServicoRepository):
        self.servico_repository = servico_repository

    async def execute(self, command: DeleteServicoCommand) -> bool:
        servico = await self.servico_repository.find_by_id(command.servico_id)

        if servico is None:
            return False

        if await self.servico_repository.has_vinculos(command.servico_id):
            raise ValueError(
                "O serviço não pode ser excluído porque está vinculado a "
                "insumos ou a ordens de serviço."
            )

        await self.servico_repository.delete(command.servico_id)

        return True
