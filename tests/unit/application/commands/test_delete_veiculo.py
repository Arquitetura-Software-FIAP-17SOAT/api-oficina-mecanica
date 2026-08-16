from unittest.mock import AsyncMock

import pytest

from application.commands.delete_veiculo import (
    DeleteVeiculoCommand,
    DeleteVeiculoUseCase,
)
from domain.entities.veiculo import Veiculo


def _veiculo():
    return Veiculo(cliente_id=1, marca_id=1, placa="ABC1D23", modelo="Gol")


@pytest.mark.asyncio
async def test_exclui_com_sucesso():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = _veiculo()
    mock_repository.has_ordens_servico.return_value = False

    use_case = DeleteVeiculoUseCase(mock_repository)
    resultado = await use_case.execute(DeleteVeiculoCommand(veiculo_id=1))

    assert resultado is True
    mock_repository.delete.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_retorna_false_quando_veiculo_nao_existe():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = DeleteVeiculoUseCase(mock_repository)
    resultado = await use_case.execute(DeleteVeiculoCommand(veiculo_id=999))

    assert resultado is False
    mock_repository.delete.assert_not_called()


@pytest.mark.asyncio
async def test_falha_quando_veiculo_possui_ordens_servico():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = _veiculo()
    mock_repository.has_ordens_servico.return_value = True

    use_case = DeleteVeiculoUseCase(mock_repository)

    with pytest.raises(ValueError, match="ordens de serviço"):
        await use_case.execute(DeleteVeiculoCommand(veiculo_id=1))

    mock_repository.delete.assert_not_called()
