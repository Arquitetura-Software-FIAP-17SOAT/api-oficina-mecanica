from dataclasses import dataclass

from domain.entities.ordem_servico import OrdemServico
from domain.repositories.ordem_servico_repository import OrdemServicoRepository
from domain.repositories.servico_repository import ServicoRepository


class ServicoNaoEncontradoError(Exception):
    """Exceção lançada quando o serviço informado não existe."""


@dataclass
class AdicionarItemOrdemServicoCommand:
    """Comando para adicionar um serviço (item) à ordem de serviço."""

    ordem_servico_id: int
    servico_id: str
    quantidade: int = 1


class AdicionarItemOrdemServicoUseCase:
    """Caso de uso para adicionar um serviço do catálogo à OS.

    Mesmo desenho de ``AdicionarInsumoOrdemServicoUseCase``: busca o preço
    através do repositório (nunca com uma query SQL solta na rota) e delega a
    validação de negócio (duplicidade, quantidade, status da OS) à entidade.
    """

    def __init__(
        self,
        ordem_servico_repository: OrdemServicoRepository,
        servico_repository: ServicoRepository,
    ):
        self.ordem_servico_repository = ordem_servico_repository
        self.servico_repository = servico_repository

    async def execute(
        self, command: AdicionarItemOrdemServicoCommand
    ) -> OrdemServico | None:
        ordem_servico = await self.ordem_servico_repository.find_by_id(
            command.ordem_servico_id
        )

        if ordem_servico is None:
            return None

        servico = await self.servico_repository.find_by_id(
            int(command.servico_id)
        )

        if servico is None:
            raise ServicoNaoEncontradoError(
                f"Serviço {command.servico_id} não encontrado"
            )

        ordem_servico.adicionar_item(
            servico_id=command.servico_id,
            valor=float(servico.valor.value),
            quantidade=command.quantidade,
        )

        return await self.ordem_servico_repository.save(ordem_servico)
