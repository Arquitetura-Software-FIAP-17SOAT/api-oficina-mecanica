from dataclasses import dataclass

from domain.entities.ordem_servico import OrdemServico
from domain.repositories.ordem_servico_repository import OrdemServicoRepository


@dataclass
class RejeitarOrcamentoOrdemServicoCommand:
    """Comando para rejeitar o orçamento e encerrar a ordem de serviço."""

    ordem_servico_id: int


class RejeitarOrcamentoOrdemServicoUseCase:
    """Rejeita o orçamento de uma OS aguardando aprovação."""

    def __init__(self, ordem_servico_repository: OrdemServicoRepository):
        self.ordem_servico_repository = ordem_servico_repository

    async def execute(
        self, command: RejeitarOrcamentoOrdemServicoCommand
    ) -> OrdemServico | None:
        ordem_servico = await self.ordem_servico_repository.find_by_id(
            command.ordem_servico_id
        )

        if ordem_servico is None:
            return None

        ordem_servico.rejeitar_orcamento()

        return await self.ordem_servico_repository.save(ordem_servico)