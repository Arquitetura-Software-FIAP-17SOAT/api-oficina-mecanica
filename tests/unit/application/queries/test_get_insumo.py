from unittest.mock import AsyncMock

import pytest

from application.queries.get_insumo import GetInsumoUseCase
from domain.entities.insumo import Insumo


@pytest.mark.asyncio
async def test_retorna_insumo_quando_encontrado():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = Insumo(nome="Óleo")

    use_case = GetInsumoUseCase(mock_repository)
    insumo = await use_case.execute(1)

    assert insumo.nome == "Óleo"
    mock_repository.find_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_retorna_none_quando_nao_encontrado():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = GetInsumoUseCase(mock_repository)
    insumo = await use_case.execute(999)

    assert insumo is None
