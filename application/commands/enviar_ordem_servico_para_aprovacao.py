from dataclasses import dataclass

from domain.entities.ordem_servico import OrdemServico
from domain.repositories.ordem_servico_repository import OrdemServicoRepository


@dataclass
class EnviarOrdemServicoParaAprovacaoCommand:
    """Comando para enviar o orçamento da ordem de serviço para aprovação."""

    ordem_servico_id: int
    orcamento: float
    observacoes: str | None = None


class EnviarOrdemServicoParaAprovacaoUseCase:
    """Caso de uso acionado quando o orçamento é gerado e enviado ao cliente.

    Move a ordem de serviço de 'Em diagnóstico' para 'Aguardando aprovação'.
    """

    def __init__(self, ordem_servico_repository: OrdemServicoRepository):
        self.ordem_servico_repository = ordem_servico_repository

    async def execute(
        self, command: EnviarOrdemServicoParaAprovacaoCommand
    ) -> OrdemServico | None:
        ordem_servico = await self.ordem_servico_repository.find_by_id(
            command.ordem_servico_id
        )

        if ordem_servico is None:
            return None

        ordem_servico.enviar_para_aprovacao(command.orcamento, command.observacoes)

        return await self.ordem_servico_repository.save(ordem_servico)
