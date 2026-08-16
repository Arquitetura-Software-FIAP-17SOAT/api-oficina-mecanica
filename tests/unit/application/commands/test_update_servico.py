from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from application.commands.update_servico import (
    UpdateServicoCommand,
    UpdateServicoUseCase,
)
from domain.entities.servico import Servico


@pytest.mark.asyncio
async def test_atualiza_com_sucesso():
    servico = Servico(id=1, nome="Troca de óleo", valor=Decimal("100.00"))
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = servico
    mock_repository.exists_by_nome.return_value = False
    mock_repository.update.side_effect = lambda s: s

    use_case = UpdateServicoUseCase(mock_repository)
    command = UpdateServicoCommand(
        servico_id=1, nome="Troca de óleo completa", valor=Decimal("150.00")
    )

    resultado = await use_case.execute(command)

    assert resultado.nome == "Troca de óleo completa"
    assert resultado.valor.value == Decimal("150.00")
    mock_repository.exists_by_nome.assert_awaited_once_with("Troca de óleo completa")


@pytest.mark.asyncio
async def test_nao_valida_duplicidade_quando_nome_nao_muda():
    servico = Servico(id=1, nome="Troca de óleo", valor=Decimal("100.00"))
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = servico
    mock_repository.update.side_effect = lambda s: s

    use_case = UpdateServicoUseCase(mock_repository)
    command = UpdateServicoCommand(
        servico_id=1, nome="Troca de óleo", valor=Decimal("130.00")
    )

    await use_case.execute(command)

    mock_repository.exists_by_nome.assert_not_awaited()


@pytest.mark.asyncio
async def test_retorna_none_quando_servico_nao_existe():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = UpdateServicoUseCase(mock_repository)
    command = UpdateServicoCommand(
        servico_id=999, nome="Troca de óleo", valor=Decimal("100.00")
    )

    resultado = await use_case.execute(command)

    assert resultado is None
    mock_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_falha_ao_renomear_para_nome_ja_existente():
    servico = Servico(id=1, nome="Troca de óleo", valor=Decimal("100.00"))
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = servico
    mock_repository.exists_by_nome.return_value = True

    use_case = UpdateServicoUseCase(mock_repository)
    command = UpdateServicoCommand(
        servico_id=1, nome="Alinhamento", valor=Decimal("100.00")
    )

    with pytest.raises(ValueError, match="Já existe um serviço"):
        await use_case.execute(command)

    mock_repository.update.assert_not_called()
