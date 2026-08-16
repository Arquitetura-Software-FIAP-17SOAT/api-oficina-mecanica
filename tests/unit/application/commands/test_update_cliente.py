from unittest.mock import AsyncMock

import pytest

from application.commands.update_cliente import (
    UpdateClienteCommand,
    UpdateClienteUseCase,
)
from domain.entities.cliente import Cliente


@pytest.mark.asyncio
async def test_atualiza_com_sucesso():
    cliente = Cliente(id=1, nome="Maria", usuario_id=1, cpf_cnpj="52998224725")
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = cliente
    mock_repository.update.side_effect = lambda c: c

    use_case = UpdateClienteUseCase(mock_repository)
    command = UpdateClienteCommand(
        cliente_id=1,
        nome="Maria Souza",
        cpf_cnpj="52998224725",
        email="maria@example.com",
    )

    resultado = await use_case.execute(command)

    assert resultado.nome == "Maria Souza"
    assert str(resultado.email) == "maria@example.com"
    mock_repository.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_retorna_none_quando_cliente_nao_existe():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = UpdateClienteUseCase(mock_repository)
    command = UpdateClienteCommand(cliente_id=999, nome="Maria")

    resultado = await use_case.execute(command)

    assert resultado is None
    mock_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_falha_ao_trocar_para_cpf_cnpj_ja_cadastrado():
    cliente = Cliente(id=1, nome="Maria", usuario_id=1, cpf_cnpj="52998224725")
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = cliente
    mock_repository.exists_by_cpf_cnpj.return_value = True

    use_case = UpdateClienteUseCase(mock_repository)
    command = UpdateClienteCommand(
        cliente_id=1, nome="Maria", cpf_cnpj="11144477735"
    )

    with pytest.raises(ValueError, match="Já existe um cliente"):
        await use_case.execute(command)

    mock_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_nao_valida_duplicidade_quando_cpf_cnpj_nao_muda():
    cliente = Cliente(id=1, nome="Maria", usuario_id=1, cpf_cnpj="52998224725")
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = cliente
    mock_repository.update.side_effect = lambda c: c

    use_case = UpdateClienteUseCase(mock_repository)
    command = UpdateClienteCommand(
        cliente_id=1, nome="Maria Souza", cpf_cnpj="52998224725"
    )

    await use_case.execute(command)

    mock_repository.exists_by_cpf_cnpj.assert_not_called()
