from unittest.mock import AsyncMock

import pytest

from application.commands.adjust_estoque import (
    AdjustEstoqueCommand,
    AdjustEstoqueUseCase,
)
from domain.entities.insumo import Insumo


@pytest.mark.asyncio
async def test_ajusta_estoque_com_sucesso():
    insumo = Insumo(nome="Pastilha de freio", estoque=10)
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = insumo
    mock_repository.update.side_effect = lambda i: i

    use_case = AdjustEstoqueUseCase(mock_repository)
    command = AdjustEstoqueCommand(insumo_id=1, quantidade=3)

    resultado = await use_case.execute(command)

    assert resultado.estoque == 3
    mock_repository.update.assert_awaited_once_with(insumo)


@pytest.mark.asyncio
async def test_retorna_none_quando_insumo_nao_encontrado():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = AdjustEstoqueUseCase(mock_repository)
    command = AdjustEstoqueCommand(insumo_id=999, quantidade=3)

    resultado = await use_case.execute(command)

    assert resultado is None
    mock_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_falha_com_quantidade_negativa():
    insumo = Insumo(nome="Pastilha de freio", estoque=10)
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = insumo

    use_case = AdjustEstoqueUseCase(mock_repository)
    command = AdjustEstoqueCommand(insumo_id=1, quantidade=-1)

    with pytest.raises(ValueError, match="não pode ser negativo"):
        await use_case.execute(command)
