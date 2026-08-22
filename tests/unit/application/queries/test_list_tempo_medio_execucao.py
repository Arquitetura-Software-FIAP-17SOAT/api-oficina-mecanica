from unittest.mock import AsyncMock

import pytest

from application.queries.list_tempo_medio_execucao import (
    ListTempoMedioExecucaoUseCase,
)


@pytest.mark.asyncio
async def test_lista_tempo_medio_execucao_arredondado():
    repository = AsyncMock()
    repository.list_tempo_medio_execucao.return_value = [
        (1, "Troca de óleo", 1.256, 3),
    ]

    use_case = ListTempoMedioExecucaoUseCase(repository)

    resultado = await use_case.execute()

    assert resultado[0].servico_id == 1
    assert resultado[0].nome_servico == "Troca de óleo"
    assert resultado[0].tempo_medio_horas == 1.26
    assert resultado[0].quantidade_execucoes == 3
    repository.list_tempo_medio_execucao.assert_awaited_once_with()