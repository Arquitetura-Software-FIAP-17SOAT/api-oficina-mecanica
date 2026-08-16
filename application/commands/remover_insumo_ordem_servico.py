from dataclasses import dataclass

from domain.entities.ordem_servico import OrdemServico
from domain.repositories.insumo_repository import InsumoRepository
from domain.repositories.ordem_servico_repository import OrdemServicoRepository


@dataclass
class RemoverInsumoOrdemServicoCommand:
    """Comando para remover uma peça/insumo avulso da ordem de serviço."""

    ordem_servico_id: int
    insumo_id: int


class RemoverInsumoOrdemServicoUseCase:
    """Caso de uso para desfazer o registro de uma peça usada na OS.

    Estorna a quantidade ao estoque do insumo — sem isso, remover um insumo
    da OS por engano deixaria o saldo permanentemente a menos do que deveria.
    """

    def __init__(
        self,
        ordem_servico_repository: OrdemServicoRepository,
        insumo_repository: InsumoRepository,
    ):
        self.ordem_servico_repository = ordem_servico_repository
        self.insumo_repository = insumo_repository

    async def execute(
        self, command: RemoverInsumoOrdemServicoCommand
    ) -> OrdemServico | None:
        ordem_servico = await self.ordem_servico_repository.find_by_id(
            command.ordem_servico_id
        )

        if ordem_servico is None:
            return None

        quantidade = ordem_servico.remover_insumo(str(command.insumo_id))

        insumo = await self.insumo_repository.find_by_id(command.insumo_id)

        if insumo is not None:
            insumo.adicionar_estoque(quantidade)
            await self.insumo_repository.update(insumo)

        return await self.ordem_servico_repository.save(ordem_servico)
