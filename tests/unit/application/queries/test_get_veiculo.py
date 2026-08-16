from unittest.mock import AsyncMock

import pytest

from application.queries.get_veiculo import GetVeiculoUseCase
from domain.entities.veiculo import Veiculo


@pytest.mark.asyncio
async def test_retorna_veiculo_quando_encontrado():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = Veiculo(
        cliente_id=1, marca_id=1, placa="ABC1D23", modelo="Gol"
    )

    use_case = GetVeiculoUseCase(mock_repository)
    veiculo = await use_case.execute(1)

    assert veiculo.modelo == "Gol"
    mock_repository.find_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_retorna_none_quando_nao_encontrado():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = GetVeiculoUseCase(mock_repository)
    veiculo = await use_case.execute(999)

    assert veiculo is None
