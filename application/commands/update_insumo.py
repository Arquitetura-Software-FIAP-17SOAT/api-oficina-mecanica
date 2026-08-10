from dataclasses import dataclass
from decimal import Decimal

from domain.entities.insumo import Insumo
from domain.repositories.insumo_repository import InsumoRepository


@dataclass
class UpdateInsumoCommand:
    """Comando para atualização de insumo."""

    insumo_id: int
    nome: str
    descricao: str | None = None
    preco_unitario: Decimal | None = None
    quantidade_minima: int = 0


class UpdateInsumoUseCase:
    """Caso de uso para atualização do cadastro de insumos."""

    def __init__(self, insumo_repository: InsumoRepository):
        self.insumo_repository = insumo_repository

    async def execute(self, command: UpdateInsumoCommand) -> Insumo | None:
        insumo = await self.insumo_repository.find_by_id(command.insumo_id)

        if insumo is None:
            return None

        if command.nome.strip() != insumo.nome:
            if await self.insumo_repository.exists_by_nome(command.nome):
                raise ValueError("Já existe um insumo cadastrado com esse nome.")

        insumo.change_nome(command.nome)
        insumo.change_descricao(command.descricao)
        insumo.change_preco_unitario(command.preco_unitario)
        insumo.change_quantidade_minima(command.quantidade_minima)

        return await self.insumo_repository.update(insumo)
