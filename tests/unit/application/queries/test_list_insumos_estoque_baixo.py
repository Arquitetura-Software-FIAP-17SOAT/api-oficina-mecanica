from unittest.mock import AsyncMock

import pytest

from application.queries.list_insumos_estoque_baixo import (
    ListInsumosEstoqueBaixoUseCase,
)
from domain.entities.insumo import Insumo


@pytest.mark.asyncio
async def test_lista_insumos_com_estoque_baixo():
    mock_repository = AsyncMock()
    mock_repository.list_estoque_baixo.return_value = [
        Insumo(nome="Óleo", estoque=1, quantidade_minima=5)
    ]

    use_case = ListInsumosEstoqueBaixoUseCase(mock_repository)
    insumos = await use_case.execute()

    assert len(insumos) == 1
    mock_repository.list_estoque_baixo.assert_awaited_once()
