from abc import ABC, abstractmethod

from domain.entities.execucao_servico import ExecucaoServico


class ExecucaoServicoRepository(ABC):
    """Contrato para persistência da execução de serviços em uma OS."""

    @abstractmethod
    def find_status_ordem(self, ordem_servico_id: int) -> str | None:
        """Status da OS, ou None se ela não existir."""
        pass

    @abstractmethod
    def find_execucao(
        self, ordem_servico_id: int, servico_id: int
    ) -> ExecucaoServico | None:
        """Execução do serviço na OS, ou None se o serviço não estiver na OS."""
        pass

    @abstractmethod
    def save(self, execucao: ExecucaoServico) -> None:
        """Persiste as datas de início/fim da execução."""
        pass
