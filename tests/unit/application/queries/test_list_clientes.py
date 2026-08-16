from unittest.mock import AsyncMock

import pytest

from application.queries.list_clientes import ListClientesUseCase
from domain.entities.cliente import Cliente


@pytest.mark.asyncio
async def test_lista_clientes():
    mock_repository = AsyncMock()
    mock_repository.list.return_value = [
        Cliente(nome="Ana", usuario_id=1),
        Cliente(nome="Bruno", usuario_id=2),
    ]

    use_case = ListClientesUseCase(mock_repository)
    clientes = await use_case.execute()

    assert len(clientes) == 2
    mock_repository.list.assert_awaited_once()


@pytest.mark.asyncio
async def test_lista_vazia_quando_nao_ha_clientes():
    mock_repository = AsyncMock()
    mock_repository.list.return_value = []

    use_case = ListClientesUseCase(mock_repository)
    clientes = await use_case.execute()

    assert clientes == []
