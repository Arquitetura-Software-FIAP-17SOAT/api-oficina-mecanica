from unittest.mock import AsyncMock

import pytest

from application.queries.list_insumos import ListInsumosUseCase
from domain.entities.insumo import Insumo


@pytest.mark.asyncio
async def test_lista_insumos():
    mock_repository = AsyncMock()
    mock_repository.list.return_value = [Insumo(nome="Óleo"), Insumo(nome="Filtro")]

    use_case = ListInsumosUseCase(mock_repository)
    insumos = await use_case.execute()

    assert len(insumos) == 2
    mock_repository.list.assert_awaited_once()
