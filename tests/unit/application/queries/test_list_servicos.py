from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from application.queries.list_servicos import ListServicosUseCase
from domain.entities.servico import Servico


@pytest.mark.asyncio
async def test_lista_servicos():
    mock_repository = AsyncMock()
    mock_repository.list.return_value = [
        Servico(nome="Troca de óleo", valor=Decimal("100.00"))
    ]

    use_case = ListServicosUseCase(mock_repository)
    servicos = await use_case.execute()

    assert len(servicos) == 1
    mock_repository.list.assert_awaited_once()
