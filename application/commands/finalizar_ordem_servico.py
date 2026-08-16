from dataclasses import dataclass

from domain.entities.ordem_servico import OrdemServico
from domain.repositories.ordem_servico_repository import OrdemServicoRepository


@dataclass
class FinalizarOrdemServicoCommand:
    """Comando para marcar a ordem de serviço como finalizada."""

    ordem_servico_id: int
    observacoes: str | None = None


class FinalizarOrdemServicoUseCase:
    """Caso de uso acionado quando o técnico conclui todos os serviços e peças.

    Move a ordem de serviço de 'Em execução' para 'Finalizada'.
    """

    def __init__(self, ordem_servico_repository: OrdemServicoRepository):
        self.ordem_servico_repository = ordem_servico_repository

    async def execute(
        self, command: FinalizarOrdemServicoCommand
    ) -> OrdemServico | None:
        ordem_servico = await self.ordem_servico_repository.find_by_id(
            command.ordem_servico_id
        )

        if ordem_servico is None:
            return None

        ordem_servico.finalizar(command.observacoes)

        return await self.ordem_servico_repository.save(ordem_servico)
