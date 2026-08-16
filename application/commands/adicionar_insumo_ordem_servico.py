from dataclasses import dataclass

from domain.entities.ordem_servico import OrdemServico
from domain.repositories.insumo_repository import InsumoRepository
from domain.repositories.ordem_servico_repository import OrdemServicoRepository


class InsumoNaoEncontradoError(Exception):
    """Exceção lançada quando o insumo informado não existe."""


@dataclass
class AdicionarInsumoOrdemServicoCommand:
    """Comando para registrar uma peça/insumo avulso usado na ordem de serviço."""

    ordem_servico_id: int
    insumo_id: int
    quantidade: int = 1


class AdicionarInsumoOrdemServicoUseCase:
    """Caso de uso para o mecânico registrar uma peça usada na OS.

    Cobre o consumo de peças que não fazem parte da composição fixa de
    nenhum serviço cadastrado (``ServicoInsumoModel``) — por exemplo, uma
    peça extra identificada durante a execução. Reaproveita o preço unitário
    e o controle de estoque já existentes em ``Insumo``
    (``Insumo.remover_estoque``, a mesma regra usada pelo CRUD de insumos), e
    persiste a baixa de estoque e o vínculo com a OS através dos respectivos
    repositórios.
    """

    def __init__(
        self,
        ordem_servico_repository: OrdemServicoRepository,
        insumo_repository: InsumoRepository,
    ):
        self.ordem_servico_repository = ordem_servico_repository
        self.insumo_repository = insumo_repository

    async def execute(
        self, command: AdicionarInsumoOrdemServicoCommand
    ) -> OrdemServico | None:
        ordem_servico = await self.ordem_servico_repository.find_by_id(
            command.ordem_servico_id
        )

        if ordem_servico is None:
            return None

        insumo = await self.insumo_repository.find_by_id(command.insumo_id)

        if insumo is None:
            raise InsumoNaoEncontradoError(
                f"Insumo {command.insumo_id} não encontrado"
            )

        insumo.remover_estoque(command.quantidade)

        ordem_servico.adicionar_insumo(
            insumo_id=str(command.insumo_id),
            valor=float(insumo.preco_unitario.value) if insumo.preco_unitario else 0.0,
            quantidade=command.quantidade,
        )

        await self.insumo_repository.update(insumo)

        return await self.ordem_servico_repository.save(ordem_servico)
