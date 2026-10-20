from dataclasses import dataclass, field
from application.commands.adicionar_insumo_ordem_servico import (
    InsumoNaoEncontradoError,
)
from application.commands.adicionar_item_ordem_servico import (
    ServicoNaoEncontradoError,
)
from application.ports.unit_of_work import UnitOfWork
from domain.entities.ordem_servico import OrdemServico
from domain.repositories.insumo_repository import InsumoRepository
from domain.repositories.ordem_servico_repository import OrdemServicoRepository
from domain.repositories.servico_repository import ServicoRepository
from domain.repositories.veiculo_repository import VeiculoRepository


@dataclass
class ServicoSolicitado:
    """Serviço do catálogo solicitado já na abertura da OS."""
    servico_id: str
    quantidade: int = 1


@dataclass
class InsumoSolicitado:
    """Peça/insumo solicitado já na abertura da OS."""
    insumo_id: int
    quantidade: int = 1


@dataclass
class CriarOrdemServicoCommand:
    """Comando para criação de ordem de serviço."""
    cliente_id: int
    veiculo_id: str
    descricao: str
    orcamento: float = None
    observacoes: str = None
    servicos: list[ServicoSolicitado] = field(default_factory=list)
    insumos: list[InsumoSolicitado] = field(default_factory=list)


class VeiculoNaoEncontradoError(Exception):
    """Exceção lançada quando um veículo não é encontrado"""
    pass


class CriarOrdemServicoUseCase:
    """Caso de uso para abertura de ordem de serviço.

    Recebe veículo (de onde vem o cliente), serviços e peças. Tudo é validado
    antes de persistir: se qualquer item falhar, nada é gravado nem baixado
    do estoque. A gravação da OS e a baixa de estoque formam uma única
    transação.
    """

    def __init__(
        self,
        ordem_servico_repository: OrdemServicoRepository,
        veiculo_repository: VeiculoRepository,
        servico_repository: ServicoRepository,
        insumo_repository: InsumoRepository,
        unit_of_work: UnitOfWork,
    ):
        self.ordem_servico_repository = ordem_servico_repository
        self.veiculo_repository = veiculo_repository
        self.servico_repository = servico_repository
        self.insumo_repository = insumo_repository
        self.unit_of_work = unit_of_work

    async def execute(self, command: CriarOrdemServicoCommand) -> OrdemServico:
        """Executa a criação da ordem de serviço"""
        # Valida se o veículo existe
        veiculo = await self.veiculo_repository.find_by_id(int(command.veiculo_id))

        if not veiculo:
            raise VeiculoNaoEncontradoError(
                f"Veículo com ID {command.veiculo_id} não encontrado no banco de dados"
            )

        if command.cliente_id != veiculo.cliente_id:
            raise ValueError("O veículo informado não pertence ao cliente informado")

        # Cria a entidade (com validações automáticas)
        ordem_servico = OrdemServico(
            veiculo_id=command.veiculo_id,
            descricao=command.descricao,
            orcamento=command.orcamento,
            observacoes=command.observacoes,
        )

        for solicitado in command.servicos:
            servico = await self.servico_repository.find_by_id(int(solicitado.servico_id))
            if servico is None:
                raise ServicoNaoEncontradoError(
                    f"Serviço {solicitado.servico_id} não encontrado"
                )
            ordem_servico.adicionar_item(
                servico_id=solicitado.servico_id,
                valor=float(servico.valor.value),
                quantidade=solicitado.quantidade,
            )

        insumos_baixados = []
        for solicitado in command.insumos:
            insumo = await self.insumo_repository.find_by_id(solicitado.insumo_id)
            if insumo is None:
                raise InsumoNaoEncontradoError(
                    f"Insumo {solicitado.insumo_id} não encontrado"
                )
            ordem_servico.adicionar_insumo(
                insumo_id=str(solicitado.insumo_id),
                valor=float(insumo.preco_unitario.value) if insumo.preco_unitario else 0.0,
                quantidade=solicitado.quantidade,
            )
            insumo.remover_estoque(solicitado.quantidade)
            insumos_baixados.append(insumo)

        # Persiste só depois de validar tudo, numa única transação: a OS e a
        # baixa de estoque são confirmadas juntas ou nenhuma delas.
        async with self.unit_of_work:
            await self.ordem_servico_repository.save(ordem_servico)

            for insumo in insumos_baixados:
                await self.insumo_repository.update(insumo)

        return ordem_servico
