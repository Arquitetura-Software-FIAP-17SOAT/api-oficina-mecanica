from unittest.mock import AsyncMock

import pytest

from application.queries.get_cliente import GetClienteUseCase
from domain.entities.cliente import Cliente


@pytest.mark.asyncio
async def test_retorna_cliente_quando_encontrado():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = Cliente(nome="Maria", usuario_id=1)

    use_case = GetClienteUseCase(mock_repository)
    cliente = await use_case.execute(1)

    assert cliente.nome == "Maria"
    mock_repository.find_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_retorna_none_quando_nao_encontrado():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = GetClienteUseCase(mock_repository)
    cliente = await use_case.execute(999)

    assert cliente is None
