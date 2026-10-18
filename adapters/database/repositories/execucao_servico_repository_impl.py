from sqlalchemy.orm import Session

from adapters.database.transaction import persistir
from domain.entities.execucao_servico import ExecucaoServico
from domain.repositories.execucao_servico_repository import ExecucaoServicoRepository
from adapters.database.models import OrdemServicoModel, OrdemServicoServicoModel


class ExecucaoServicoRepositoryImpl(ExecucaoServicoRepository):
    """Persistência da execução de serviços em uma OS."""

    def __init__(self, db: Session):
        self.db = db

    def find_status_ordem(self, ordem_servico_id: int) -> str | None:
        ordem = self.db.get(OrdemServicoModel, ordem_servico_id)

        return ordem.status if ordem else None

    def _find_model(
        self, ordem_servico_id: int, servico_id: int
    ) -> OrdemServicoServicoModel | None:
        return self.db.get(OrdemServicoServicoModel, (ordem_servico_id, servico_id))

    def find_execucao(
        self, ordem_servico_id: int, servico_id: int
    ) -> ExecucaoServico | None:
        model = self._find_model(ordem_servico_id, servico_id)
        if model is None:
            return None

        return ExecucaoServico(
            ordem_servico_id=model.ordem_servico_id,
            servico_id=model.servico_id,
            data_inicio=model.data_inicio,
            data_fim=model.data_fim,
        )

    def save(self, execucao: ExecucaoServico) -> None:
        model = self._find_model(execucao.ordem_servico_id, execucao.servico_id)
        model.data_inicio = execucao.data_inicio
        model.data_fim = execucao.data_fim
        persistir(self.db)
