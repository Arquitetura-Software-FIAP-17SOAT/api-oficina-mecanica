from dataclasses import dataclass, field

from domain.entities.cliente import Cliente
from domain.entities.insumo import Insumo
from domain.entities.ordem_servico import OrdemServico
from domain.entities.servico import Servico
from domain.entities.veiculo import Veiculo
from domain.repositories.cliente_repository import ClienteRepository
from domain.repositories.insumo_repository import InsumoRepository
from domain.repositories.ordem_servico_repository import OrdemServicoRepository
from domain.repositories.servico_repository import ServicoRepository
from domain.repositories.veiculo_repository import VeiculoRepository


@dataclass
class ItemServicoDetalhado:
    """Um serviço adicionado à OS, com as peças/insumos que ele consome."""

    servico: Servico | None
    servico_id: str
    quantidade: int
    valor_unitario: float
    insumos: list[Insumo] = field(default_factory=list)

    @property
    def valor_total(self) -> float:
        return self.valor_unitario * self.quantidade


@dataclass
class InsumoUtilizadoDetalhado:
    """Uma peça/insumo avulso registrado diretamente na OS.

    Diferente dos insumos em ``ItemServicoDetalhado.insumos`` (a composição
    fixa de um serviço), este é o consumo registrado à parte — fora da
    receita de qualquer serviço cadastrado.
    """

    insumo: Insumo | None
    insumo_id: str
    quantidade: int
    valor_unitario: float

    @property
    def valor_total(self) -> float:
        return self.valor_unitario * self.quantidade


@dataclass
class OrdemServicoDetalhada:
    """Visão completa de uma OS: veículo, cliente, itens e insumos usados."""

    ordem_servico: OrdemServico
    veiculo: Veiculo | None
    cliente: Cliente | None
    itens: list[ItemServicoDetalhado] = field(default_factory=list)
    insumos_utilizados: list[InsumoUtilizadoDetalhado] = field(default_factory=list)

    @property
    def valor_total_itens(self) -> float:
        """Total dos serviços e peças avulsas da OS.

        Delega o cálculo à entidade — a regra do orçamento automático vive em
        ``OrdemServico.orcamento_calculado``, não é reimplementada aqui.
        """
        return self.ordem_servico.orcamento_calculado


class GetOrdemServicoDetalhadaUseCase:
    """Caso de uso para consulta detalhada de uma ordem de serviço.

    Agrega dados de outros agregados (veículo, cliente, serviços e seus
    insumos) através dos respectivos repositórios — a orquestração fica no
    caso de uso, mantendo cada entidade de domínio focada em sua própria
    responsabilidade.
    """

    def __init__(
        self,
        ordem_servico_repository: OrdemServicoRepository,
        veiculo_repository: VeiculoRepository,
        cliente_repository: ClienteRepository,
        servico_repository: ServicoRepository,
        insumo_repository: InsumoRepository,
    ):
        self.ordem_servico_repository = ordem_servico_repository
        self.veiculo_repository = veiculo_repository
        self.cliente_repository = cliente_repository
        self.servico_repository = servico_repository
        self.insumo_repository = insumo_repository

    async def execute(self, ordem_id: int) -> OrdemServicoDetalhada | None:
        ordem_servico = await self.ordem_servico_repository.find_by_id(ordem_id)

        if ordem_servico is None:
            return None

        veiculo = await self.veiculo_repository.find_by_id(
            int(ordem_servico.veiculo_id)
        )

        cliente = None
        if veiculo is not None:
            cliente = await self.cliente_repository.find_by_id(veiculo.cliente_id)

        itens_detalhados = [
            await self._detalhar_item(item) for item in ordem_servico.itens
        ]
        insumos_detalhados = [
            await self._detalhar_insumo_utilizado(item)
            for item in ordem_servico.insumos_utilizados
        ]

        return OrdemServicoDetalhada(
            ordem_servico=ordem_servico,
            veiculo=veiculo,
            cliente=cliente,
            itens=itens_detalhados,
            insumos_utilizados=insumos_detalhados,
        )

    async def _detalhar_item(self, item: dict) -> ItemServicoDetalhado:
        servico_id = int(item["servico_id"])

        servico = await self.servico_repository.find_by_id(servico_id)
        insumos = await self.insumo_repository.list_by_servico_id(servico_id)

        return ItemServicoDetalhado(
            servico=servico,
            servico_id=item["servico_id"],
            quantidade=item["quantidade"],
            valor_unitario=item["valor"],
            insumos=insumos,
        )

    async def _detalhar_insumo_utilizado(
        self, item: dict
    ) -> InsumoUtilizadoDetalhado:
        insumo = await self.insumo_repository.find_by_id(int(item["insumo_id"]))

        return InsumoUtilizadoDetalhado(
            insumo=insumo,
            insumo_id=item["insumo_id"],
            quantidade=item["quantidade"],
            valor_unitario=item["valor"],
        )
