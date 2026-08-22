from dataclasses import dataclass

from domain.repositories.servico_repository import ServicoRepository


@dataclass(frozen=True)
class TempoMedioExecucao:
    """Métrica de tempo das execuções concluídas de um serviço."""

    servico_id: int
    nome_servico: str
    tempo_medio_horas: float
    quantidade_execucoes: int


class ListTempoMedioExecucaoUseCase:
    """Caso de uso para consultar o tempo médio por serviço."""

    def __init__(self, servico_repository: ServicoRepository):
        self.servico_repository = servico_repository

    async def execute(self) -> list[TempoMedioExecucao]:
        resultados = await self.servico_repository.list_tempo_medio_execucao()

        return [
            TempoMedioExecucao(
                servico_id=servico_id,
                nome_servico=nome_servico,
                tempo_medio_horas=round(tempo_medio_horas, 2),
                quantidade_execucoes=quantidade_execucoes,
            )
            for (
                servico_id,
                nome_servico,
                tempo_medio_horas,
                quantidade_execucoes,
            ) in resultados
        ]