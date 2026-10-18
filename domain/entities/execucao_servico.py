from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExecucaoServico:
    """Execução de um serviço dentro de uma OS (início e fim registrados)."""

    ordem_servico_id: int
    servico_id: int
    data_inicio: datetime | None = None
    data_fim: datetime | None = None
