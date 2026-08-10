from unittest.mock import AsyncMock

import pytest

from application.commands.remove_estoque import (
    RemoveEstoqueCommand,
    RemoveEstoqueUseCase,
)
from domain.entities.insumo import Insumo


@pytest.mark.asyncio
async def test_saida_de_estoque_com_sucesso():
    """Testa a baixa de estoque dentro do saldo disponível."""

    # Arrange
    insumo = Insumo(nome="Pastilha de freio", estoque=10, id=1)

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = insumo

    use_case = RemoveEstoqueUseCase(mock_repository)

    # Act
    await use_case.execute(RemoveEstoqueCommand(insumo_id=1, quantidade=4))

    # Assert
    assert insumo.estoque == 6
    mock_repository.update.assert_awaited_once_with(insumo)


@pytest.mark.asyncio
async def test_saida_de_insumo_inexistente_retorna_none():
    """Testa que um insumo inexistente não gera erro, e sim ausência."""

    # Arrange
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = RemoveEstoqueUseCase(mock_repository)

    # Act
    resultado = await use_case.execute(
        RemoveEstoqueCommand(insumo_id=999, quantidade=1)
    )

    # Assert
    assert resultado is None
    mock_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_saida_maior_que_saldo_nao_persiste():
    """Testa que a regra da entidade impede a baixa e nada é salvo."""

    # Arrange
    insumo = Insumo(nome="Pastilha de freio", estoque=3, id=1)

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = insumo

    use_case = RemoveEstoqueUseCase(mock_repository)

    # Act / Assert
    with pytest.raises(ValueError, match="Estoque insuficiente"):
        await use_case.execute(RemoveEstoqueCommand(insumo_id=1, quantidade=4))

    assert insumo.estoque == 3
    mock_repository.update.assert_not_called()
