from unittest.mock import AsyncMock

import pytest

from application.commands.delete_insumo import (
    DeleteInsumoCommand,
    DeleteInsumoUseCase,
)
from domain.entities.insumo import Insumo


@pytest.mark.asyncio
async def test_exclui_com_sucesso():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = Insumo(nome="Óleo")
    mock_repository.has_vinculos.return_value = False

    use_case = DeleteInsumoUseCase(mock_repository)
    resultado = await use_case.execute(DeleteInsumoCommand(insumo_id=1))

    assert resultado is True
    mock_repository.delete.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_retorna_false_quando_insumo_nao_existe():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = DeleteInsumoUseCase(mock_repository)
    resultado = await use_case.execute(DeleteInsumoCommand(insumo_id=999))

    assert resultado is False
    mock_repository.delete.assert_not_called()


@pytest.mark.asyncio
async def test_falha_quando_insumo_possui_vinculos():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = Insumo(nome="Óleo")
    mock_repository.has_vinculos.return_value = True

    use_case = DeleteInsumoUseCase(mock_repository)

    with pytest.raises(ValueError, match="vinculado"):
        await use_case.execute(DeleteInsumoCommand(insumo_id=1))

    mock_repository.delete.assert_not_called()
