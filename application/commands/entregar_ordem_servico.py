from dataclasses import dataclass

from domain.entities.ordem_servico import OrdemServico
from domain.repositories.ordem_servico_repository import OrdemServicoRepository


@dataclass
class EntregarOrdemServicoCommand:
    """Comando para registrar a entrega do veículo ao cliente."""

    ordem_servico_id: int
    observacoes: str | None = None


class EntregarOrdemServicoUseCase:
    """Caso de uso acionado quando o veículo é retirado pelo cliente.

    Move a ordem de serviço de 'Finalizada' para 'Entregue' (estado final).
    """

    def __init__(self, ordem_servico_repository: OrdemServicoRepository):
        self.ordem_servico_repository = ordem_servico_repository

    async def execute(
        self, command: EntregarOrdemServicoCommand
    ) -> OrdemServico | None:
        ordem_servico = await self.ordem_servico_repository.find_by_id(
            command.ordem_servico_id
        )

        if ordem_servico is None:
            return None

        ordem_servico.entregar(command.observacoes)

        return await self.ordem_servico_repository.save(ordem_servico)
