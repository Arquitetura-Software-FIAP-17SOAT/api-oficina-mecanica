from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from application.commands.create_servico import (
    CreateServicoCommand,
    CreateServicoUseCase,
)


@pytest.mark.asyncio
async def test_cadastro_com_sucesso():
    mock_repository = AsyncMock()
    mock_repository.exists_by_nome.return_value = False
    mock_repository.save.side_effect = lambda servico: servico

    use_case = CreateServicoUseCase(mock_repository)
    command = CreateServicoCommand(
        nome="Troca de óleo",
        valor=Decimal("120.00"),
        descricao="Inclui filtro",
        tempo_estimado="1h",
    )

    servico = await use_case.execute(command)

    assert servico.nome == "Troca de óleo"
    assert servico.valor.value == Decimal("120.00")
    mock_repository.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_falha_com_nome_duplicado():
    mock_repository = AsyncMock()
    mock_repository.exists_by_nome.return_value = True

    use_case = CreateServicoUseCase(mock_repository)
    command = CreateServicoCommand(nome="Troca de óleo", valor=Decimal("120.00"))

    with pytest.raises(ValueError, match="Já existe um serviço"):
        await use_case.execute(command)

    mock_repository.save.assert_not_called()
