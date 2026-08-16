from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from application.queries.get_servico import GetServicoUseCase
from domain.entities.servico import Servico


@pytest.mark.asyncio
async def test_retorna_servico_quando_encontrado():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = Servico(
        nome="Troca de óleo", valor=Decimal("100.00")
    )

    use_case = GetServicoUseCase(mock_repository)
    servico = await use_case.execute(1)

    assert servico.nome == "Troca de óleo"
    mock_repository.find_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_retorna_none_quando_nao_encontrado():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = GetServicoUseCase(mock_repository)
    servico = await use_case.execute(999)

    assert servico is None
