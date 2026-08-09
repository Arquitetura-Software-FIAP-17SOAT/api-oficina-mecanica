from dataclasses import dataclass
from decimal import Decimal

from domain.entities.servico import Servico
from domain.repositories.servico_repository import ServicoRepository


@dataclass
class UpdateServicoCommand:
    """Comando para atualização de serviço."""

    servico_id: int
    nome: str
    valor: Decimal
    descricao: str | None = None
    tempo_estimado: str | None = None


class UpdateServicoUseCase:
    """Caso de uso para atualização de serviços."""

    def __init__(self, servico_repository: ServicoRepository):
        self.servico_repository = servico_repository

    async def execute(self, command: UpdateServicoCommand) -> Servico | None:
        servico = await self.servico_repository.find_by_id(command.servico_id)

        if servico is None:
            return None

        if command.nome.strip() != servico.nome:
            if await self.servico_repository.exists_by_nome(command.nome):
                raise ValueError("Já existe um serviço cadastrado com esse nome.")

        servico.change_nome(command.nome)
        servico.change_valor(command.valor)
        servico.change_descricao(command.descricao)
        servico.change_tempo_estimado(command.tempo_estimado)

        return await self.servico_repository.update(servico)
