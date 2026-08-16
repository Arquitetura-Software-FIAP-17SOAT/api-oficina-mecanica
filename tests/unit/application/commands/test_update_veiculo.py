from unittest.mock import AsyncMock

import pytest

from application.commands.update_veiculo import (
    UpdateVeiculoCommand,
    UpdateVeiculoUseCase,
)
from domain.entities.veiculo import Veiculo


@pytest.mark.asyncio
async def test_atualiza_com_sucesso():
    veiculo = Veiculo(id=1, cliente_id=1, marca_id=1, placa="ABC1D23", modelo="Gol")
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = veiculo
    mock_repository.marca_exists.return_value = True
    mock_repository.update.side_effect = lambda v: v

    use_case = UpdateVeiculoUseCase(mock_repository)
    command = UpdateVeiculoCommand(
        veiculo_id=1, marca_id=1, placa="ABC1D23", modelo="Gol 1.6"
    )

    resultado = await use_case.execute(command)

    assert resultado.modelo == "Gol 1.6"
    mock_repository.exists_by_placa.assert_not_awaited()


@pytest.mark.asyncio
async def test_retorna_none_quando_veiculo_nao_existe():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = UpdateVeiculoUseCase(mock_repository)
    command = UpdateVeiculoCommand(
        veiculo_id=999, marca_id=1, placa="ABC1D23", modelo="Gol"
    )

    resultado = await use_case.execute(command)

    assert resultado is None
    mock_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_falha_quando_marca_nao_existe():
    veiculo = Veiculo(id=1, cliente_id=1, marca_id=1, placa="ABC1D23", modelo="Gol")
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = veiculo
    mock_repository.marca_exists.return_value = False

    use_case = UpdateVeiculoUseCase(mock_repository)
    command = UpdateVeiculoCommand(
        veiculo_id=1, marca_id=999, placa="ABC1D23", modelo="Gol"
    )

    with pytest.raises(ValueError, match="Marca não encontrada"):
        await use_case.execute(command)

    mock_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_falha_ao_trocar_para_placa_ja_cadastrada():
    veiculo = Veiculo(id=1, cliente_id=1, marca_id=1, placa="ABC1D23", modelo="Gol")
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = veiculo
    mock_repository.marca_exists.return_value = True
    mock_repository.exists_by_placa.return_value = True

    use_case = UpdateVeiculoUseCase(mock_repository)
    command = UpdateVeiculoCommand(
        veiculo_id=1, marca_id=1, placa="XYZ9A87", modelo="Gol"
    )

    with pytest.raises(ValueError, match="Já existe um veículo"):
        await use_case.execute(command)

    mock_repository.update.assert_not_called()
