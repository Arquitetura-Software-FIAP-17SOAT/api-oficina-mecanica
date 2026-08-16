from dataclasses import dataclass

from domain.entities.ordem_servico import OrdemServico
from domain.repositories.ordem_servico_repository import OrdemServicoRepository


@dataclass
class RetornarOrdemServicoParaDiagnosticoCommand:
    """Comando para devolver a ordem de serviço ao diagnóstico."""

    ordem_servico_id: int
    motivo: str | None = None


class RetornarOrdemServicoParaDiagnosticoUseCase:
    """Caso de uso acionado quando o cliente não aprova o orçamento.

    Move a ordem de serviço de 'Aguardando aprovação' de volta para
    'Em diagnóstico'.
    """

    def __init__(self, ordem_servico_repository: OrdemServicoRepository):
        self.ordem_servico_repository = ordem_servico_repository

    async def execute(
        self, command: RetornarOrdemServicoParaDiagnosticoCommand
    ) -> OrdemServico | None:
        ordem_servico = await self.ordem_servico_repository.find_by_id(
            command.ordem_servico_id
        )

        if ordem_servico is None:
            return None

        ordem_servico.retornar_para_diagnostico(command.motivo)

        return await self.ordem_servico_repository.save(ordem_servico)
