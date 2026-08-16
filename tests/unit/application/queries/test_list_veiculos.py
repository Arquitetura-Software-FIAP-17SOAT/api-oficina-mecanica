from unittest.mock import AsyncMock

import pytest

from application.queries.list_veiculos import ListVeiculosUseCase
from domain.entities.veiculo import Veiculo


@pytest.mark.asyncio
async def test_lista_todos_os_veiculos():
    mock_repository = AsyncMock()
    mock_repository.list.return_value = [
        Veiculo(cliente_id=1, marca_id=1, placa="ABC1D23", modelo="Gol")
    ]

    use_case = ListVeiculosUseCase(mock_repository)
    veiculos = await use_case.execute()

    assert len(veiculos) == 1
    mock_repository.list.assert_awaited_once_with(cliente_id=None)


@pytest.mark.asyncio
async def test_lista_veiculos_filtrando_por_cliente():
    mock_repository = AsyncMock()
    mock_repository.list.return_value = []

    use_case = ListVeiculosUseCase(mock_repository)
    await use_case.execute(cliente_id=7)

    mock_repository.list.assert_awaited_once_with(cliente_id=7)
