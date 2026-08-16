from dataclasses import dataclass

from domain.entities.ordem_servico import OrdemServico
from domain.repositories.ordem_servico_repository import OrdemServicoRepository


@dataclass
class IniciarDiagnosticoOrdemServicoCommand:
    """Comando para iniciar o diagnóstico técnico de uma ordem de serviço."""

    ordem_servico_id: int
    observacoes: str | None = None


class IniciarDiagnosticoOrdemServicoUseCase:
    """Caso de uso acionado quando o mecânico inicia a avaliação técnica.

    Move a ordem de serviço de 'Recebida' para 'Em diagnóstico'.
    """

    def __init__(self, ordem_servico_repository: OrdemServicoRepository):
        self.ordem_servico_repository = ordem_servico_repository

    async def execute(
        self, command: IniciarDiagnosticoOrdemServicoCommand
    ) -> OrdemServico | None:
        ordem_servico = await self.ordem_servico_repository.find_by_id(
            command.ordem_servico_id
        )

        if ordem_servico is None:
            return None

        ordem_servico.iniciar_diagnostico(command.observacoes)

        return await self.ordem_servico_repository.save(ordem_servico)
