from dataclasses import dataclass

from domain.entities.ordem_servico import OrdemServico
from domain.repositories.ordem_servico_repository import OrdemServicoRepository


@dataclass
class RemoverItemOrdemServicoCommand:
    """Comando para remover um serviço (item) da ordem de serviço."""

    ordem_servico_id: int
    servico_id: str


class RemoverItemOrdemServicoUseCase:
    """Caso de uso para remover um serviço já adicionado à OS."""

    def __init__(self, ordem_servico_repository: OrdemServicoRepository):
        self.ordem_servico_repository = ordem_servico_repository

    async def execute(
        self, command: RemoverItemOrdemServicoCommand
    ) -> OrdemServico | None:
        ordem_servico = await self.ordem_servico_repository.find_by_id(
            command.ordem_servico_id
        )

        if ordem_servico is None:
            return None

        ordem_servico.remover_item(command.servico_id)

        return await self.ordem_servico_repository.save(ordem_servico)
