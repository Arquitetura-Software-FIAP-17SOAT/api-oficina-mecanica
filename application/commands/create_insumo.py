from dataclasses import dataclass
from decimal import Decimal

from domain.entities.insumo import Insumo
from domain.repositories.insumo_repository import InsumoRepository


@dataclass
class CreateInsumoCommand:
    nome: str
    descricao: str | None = None
    preco_unitario: Decimal | None = None
    estoque: int = 0
    quantidade_minima: int = 0


class CreateInsumoUseCase:
    def __init__(self, insumo_repository: InsumoRepository):
        self.insumo_repository = insumo_repository

    async def execute(self, command: CreateInsumoCommand) -> Insumo:
        if await self.insumo_repository.exists_by_nome(command.nome):
            raise ValueError("Já existe um insumo cadastrado com esse nome.")

        insumo = Insumo(
            nome=command.nome,
            descricao=command.descricao,
            preco_unitario=command.preco_unitario,
            estoque=command.estoque,
            quantidade_minima=command.quantidade_minima,
        )

        return await self.insumo_repository.save(insumo)
