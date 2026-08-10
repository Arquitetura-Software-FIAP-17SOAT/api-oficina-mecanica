from dataclasses import dataclass
from sqlalchemy.orm import Session
from domain.entities.ordem_servico import OrdemServico
from domain.repositories.ordem_servico_repository import OrdemServicoRepository
from infrastructure.database.models import VeiculoModel


@dataclass
class CriarOrdemServicoCommand:
    """Comando para criação de ordem de serviço."""
    veiculo_id: str
    descricao: str
    orcamento: float = None
    observacoes: str = None


class VeiculoNaoEncontradoError(Exception):
    """Exceção lançada quando um veículo não é encontrado"""
    pass


class CriarOrdemServicoUseCase:
    """Caso de uso para criação de ordem de serviço."""

    def __init__(self, ordem_servico_repository: OrdemServicoRepository, db: Session):
        self.ordem_servico_repository = ordem_servico_repository
        self.db = db

    async def execute(self, command: CriarOrdemServicoCommand) -> OrdemServico:
        """Executa a criação da ordem de serviço"""
        # Valida se o veículo existe
        veiculo = self.db.query(VeiculoModel).filter(
            VeiculoModel.id == int(command.veiculo_id)
        ).first()

        if not veiculo:
            raise VeiculoNaoEncontradoError(
                f"Veículo com ID {command.veiculo_id} não encontrado no banco de dados"
            )

        # Cria a entidade (com validações automáticas)
        ordem_servico = OrdemServico(
            veiculo_id=command.veiculo_id,
            descricao=command.descricao,
            orcamento=command.orcamento,
            observacoes=command.observacoes,
        )

        # Persiste no banco
        await self.ordem_servico_repository.save(ordem_servico)

        return ordem_servico