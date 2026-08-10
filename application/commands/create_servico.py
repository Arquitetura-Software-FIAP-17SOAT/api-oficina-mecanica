from dataclasses import dataclass
from decimal import Decimal

from domain.entities.servico import Servico
from domain.repositories.servico_repository import ServicoRepository


@dataclass
class CreateServicoCommand:
    nome: str
    valor: Decimal
    descricao: str | None = None
    tempo_estimado: str | None = None


class CreateServicoUseCase:
    def __init__(self, servico_repository: ServicoRepository):
        self.servico_repository = servico_repository

    async def execute(self, command: CreateServicoCommand) -> Servico:
        if await self.servico_repository.exists_by_nome(command.nome):
            raise ValueError("Já existe um serviço cadastrado com esse nome.")

        servico = Servico(
            nome=command.nome,
            valor=command.valor,
            descricao=command.descricao,
            tempo_estimado=command.tempo_estimado,
        )

        return await self.servico_repository.save(servico)
