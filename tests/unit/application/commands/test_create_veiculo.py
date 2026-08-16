from unittest.mock import AsyncMock

import pytest

from application.commands.create_veiculo import (
    CreateVeiculoCommand,
    CreateVeiculoUseCase,
)
from domain.entities.cliente import Cliente


def _command(**overrides):
    dados = dict(
        cliente_id=1,
        marca_id=1,
        placa="ABC1D23",
        modelo="Gol 1.0",
        chassi=None,
        ano_fabricacao=2020,
    )
    dados.update(overrides)
    return CreateVeiculoCommand(**dados)


@pytest.mark.asyncio
async def test_cadastro_com_sucesso():
    mock_veiculo_repository = AsyncMock()
    mock_cliente_repository = AsyncMock()
    mock_cliente_repository.find_by_id.return_value = Cliente(
        nome="Maria", usuario_id=1
    )
    mock_veiculo_repository.marca_exists.return_value = True
    mock_veiculo_repository.exists_by_placa.return_value = False
    mock_veiculo_repository.save.side_effect = lambda v: v

    use_case = CreateVeiculoUseCase(mock_veiculo_repository, mock_cliente_repository)

    veiculo = await use_case.execute(_command())

    assert str(veiculo.placa) == "ABC1D23"
    mock_veiculo_repository.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_falha_quando_cliente_nao_existe():
    mock_veiculo_repository = AsyncMock()
    mock_cliente_repository = AsyncMock()
    mock_cliente_repository.find_by_id.return_value = None

    use_case = CreateVeiculoUseCase(mock_veiculo_repository, mock_cliente_repository)

    with pytest.raises(ValueError, match="Cliente não encontrado"):
        await use_case.execute(_command())

    mock_veiculo_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_falha_quando_marca_nao_existe():
    mock_veiculo_repository = AsyncMock()
    mock_cliente_repository = AsyncMock()
    mock_cliente_repository.find_by_id.return_value = Cliente(
        nome="Maria", usuario_id=1
    )
    mock_veiculo_repository.marca_exists.return_value = False

    use_case = CreateVeiculoUseCase(mock_veiculo_repository, mock_cliente_repository)

    with pytest.raises(ValueError, match="Marca não encontrada"):
        await use_case.execute(_command())

    mock_veiculo_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_falha_com_placa_duplicada():
    mock_veiculo_repository = AsyncMock()
    mock_cliente_repository = AsyncMock()
    mock_cliente_repository.find_by_id.return_value = Cliente(
        nome="Maria", usuario_id=1
    )
    mock_veiculo_repository.marca_exists.return_value = True
    mock_veiculo_repository.exists_by_placa.return_value = True

    use_case = CreateVeiculoUseCase(mock_veiculo_repository, mock_cliente_repository)

    with pytest.raises(ValueError, match="Já existe um veículo"):
        await use_case.execute(_command())

    mock_veiculo_repository.save.assert_not_called()
