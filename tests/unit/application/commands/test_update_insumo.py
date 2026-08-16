from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from application.commands.update_insumo import (
    UpdateInsumoCommand,
    UpdateInsumoUseCase,
)
from domain.entities.insumo import Insumo


@pytest.mark.asyncio
async def test_atualiza_com_sucesso():
    insumo = Insumo(id=1, nome="Óleo 5W30", preco_unitario=Decimal("40.00"))
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = insumo
    mock_repository.exists_by_nome.return_value = False
    mock_repository.update.side_effect = lambda i: i

    use_case = UpdateInsumoUseCase(mock_repository)
    command = UpdateInsumoCommand(
        insumo_id=1,
        nome="Óleo 5W30 sintético",
        preco_unitario=Decimal("45.00"),
        quantidade_minima=5,
    )

    resultado = await use_case.execute(command)

    assert resultado.nome == "Óleo 5W30 sintético"
    assert resultado.quantidade_minima == 5
    mock_repository.exists_by_nome.assert_awaited_once_with("Óleo 5W30 sintético")
    mock_repository.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_retorna_none_quando_insumo_nao_existe():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = UpdateInsumoUseCase(mock_repository)
    command = UpdateInsumoCommand(insumo_id=999, nome="Óleo")

    resultado = await use_case.execute(command)

    assert resultado is None
    mock_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_falha_ao_renomear_para_nome_ja_existente():
    insumo = Insumo(id=1, nome="Óleo 5W30")
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = insumo
    mock_repository.exists_by_nome.return_value = True

    use_case = UpdateInsumoUseCase(mock_repository)
    command = UpdateInsumoCommand(insumo_id=1, nome="Óleo 5W40")

    with pytest.raises(ValueError, match="Já existe um insumo"):
        await use_case.execute(command)

    mock_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_nao_valida_duplicidade_quando_nome_nao_muda():
    insumo = Insumo(id=1, nome="Óleo 5W30")
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = insumo
    mock_repository.update.side_effect = lambda i: i

    use_case = UpdateInsumoUseCase(mock_repository)
    command = UpdateInsumoCommand(insumo_id=1, nome="Óleo 5W30")

    await use_case.execute(command)

    mock_repository.exists_by_nome.assert_not_awaited()
