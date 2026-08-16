from unittest.mock import AsyncMock

import pytest

from application.commands.delete_cliente import (
    DeleteClienteCommand,
    DeleteClienteUseCase,
)
from domain.entities.cliente import Cliente


@pytest.mark.asyncio
async def test_exclui_com_sucesso():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = Cliente(nome="Maria", usuario_id=1)
    mock_repository.has_veiculos.return_value = False

    use_case = DeleteClienteUseCase(mock_repository)
    resultado = await use_case.execute(DeleteClienteCommand(cliente_id=1))

    assert resultado is True
    mock_repository.delete.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_retorna_false_quando_cliente_nao_existe():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = DeleteClienteUseCase(mock_repository)
    resultado = await use_case.execute(DeleteClienteCommand(cliente_id=999))

    assert resultado is False
    mock_repository.delete.assert_not_called()


@pytest.mark.asyncio
async def test_falha_quando_cliente_possui_veiculos():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = Cliente(nome="Maria", usuario_id=1)
    mock_repository.has_veiculos.return_value = True

    use_case = DeleteClienteUseCase(mock_repository)

    with pytest.raises(ValueError, match="possui veículos"):
        await use_case.execute(DeleteClienteCommand(cliente_id=1))

    mock_repository.delete.assert_not_called()
