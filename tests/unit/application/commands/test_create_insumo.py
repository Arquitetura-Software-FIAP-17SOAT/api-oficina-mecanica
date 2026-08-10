from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from application.commands.create_insumo import (
    CreateInsumoCommand,
    CreateInsumoUseCase,
)


@pytest.mark.asyncio
async def test_cadastro_com_sucesso():
    """Testa o cadastro de um insumo com dados válidos."""

    # Arrange
    mock_repository = AsyncMock()
    mock_repository.exists_by_nome.return_value = False

    use_case = CreateInsumoUseCase(mock_repository)

    command = CreateInsumoCommand(
        nome="Filtro de óleo",
        preco_unitario=Decimal("32.50"),
        estoque=20,
        quantidade_minima=5,
    )

    # Act
    await use_case.execute(command)

    # Assert
    mock_repository.exists_by_nome.assert_awaited_once_with("Filtro de óleo")
    mock_repository.save.assert_awaited_once()

    insumo = mock_repository.save.await_args.args[0]
    assert insumo.nome == "Filtro de óleo"
    assert insumo.estoque == 20
    assert insumo.quantidade_minima == 5


@pytest.mark.asyncio
async def test_cadastro_falha_com_nome_duplicado():
    """Testa a tentativa de cadastrar um insumo com nome já existente."""

    # Arrange
    mock_repository = AsyncMock()
    mock_repository.exists_by_nome.return_value = True

    use_case = CreateInsumoUseCase(mock_repository)

    command = CreateInsumoCommand(nome="Filtro de óleo")

    # Act / Assert
    with pytest.raises(ValueError, match="Já existe um insumo"):
        await use_case.execute(command)

    mock_repository.save.assert_not_called()
