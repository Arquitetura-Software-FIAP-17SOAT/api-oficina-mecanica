from unittest.mock import AsyncMock

import pytest

from application.commands.add_estoque import AddEstoqueCommand, AddEstoqueUseCase
from domain.entities.insumo import Insumo


@pytest.mark.asyncio
async def test_adiciona_estoque_com_sucesso():
    insumo = Insumo(nome="Filtro de óleo", estoque=10, quantidade_minima=2)
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = insumo
    mock_repository.update.side_effect = lambda i: i

    use_case = AddEstoqueUseCase(mock_repository)
    command = AddEstoqueCommand(insumo_id=1, quantidade=5)

    resultado = await use_case.execute(command)

    mock_repository.find_by_id.assert_awaited_once_with(1)
    assert resultado.estoque == 15
    mock_repository.update.assert_awaited_once_with(insumo)


@pytest.mark.asyncio
async def test_retorna_none_quando_insumo_nao_encontrado():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = AddEstoqueUseCase(mock_repository)
    command = AddEstoqueCommand(insumo_id=999, quantidade=5)

    resultado = await use_case.execute(command)

    assert resultado is None
    mock_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_falha_com_quantidade_invalida():
    insumo = Insumo(nome="Filtro de óleo", estoque=10)
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = insumo

    use_case = AddEstoqueUseCase(mock_repository)
    command = AddEstoqueCommand(insumo_id=1, quantidade=0)

    with pytest.raises(ValueError, match="maior que zero"):
        await use_case.execute(command)

    mock_repository.update.assert_not_called()
