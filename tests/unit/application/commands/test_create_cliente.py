from unittest.mock import AsyncMock

import pytest

from application.commands.create_cliente import (
    CreateClienteCommand,
    CreateClienteUseCase,
)
from domain.entities.usuario import Usuario


@pytest.mark.asyncio
async def test_cadastro_com_sucesso():
    mock_cliente_repository = AsyncMock()
    mock_user_repository = AsyncMock()
    mock_user_repository.find_by_id.return_value = Usuario(
        name="João", email="joao@example.com", hashed_password="hash"
    )
    mock_cliente_repository.exists_by_cpf_cnpj.return_value = False
    mock_cliente_repository.save.side_effect = lambda cliente: cliente

    use_case = CreateClienteUseCase(mock_cliente_repository, mock_user_repository)
    command = CreateClienteCommand(
        nome="Maria Souza",
        usuario_id=1,
        cpf_cnpj="52998224725",
        email="maria@example.com",
    )

    cliente = await use_case.execute(command)

    assert cliente.nome == "Maria Souza"
    mock_cliente_repository.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_falha_quando_usuario_responsavel_nao_existe():
    mock_cliente_repository = AsyncMock()
    mock_user_repository = AsyncMock()
    mock_user_repository.find_by_id.return_value = None

    use_case = CreateClienteUseCase(mock_cliente_repository, mock_user_repository)
    command = CreateClienteCommand(nome="Maria Souza", usuario_id=999)

    with pytest.raises(ValueError, match="Usuário responsável não encontrado"):
        await use_case.execute(command)

    mock_cliente_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_falha_com_cpf_cnpj_duplicado():
    mock_cliente_repository = AsyncMock()
    mock_user_repository = AsyncMock()
    mock_user_repository.find_by_id.return_value = Usuario(
        name="João", email="joao@example.com", hashed_password="hash"
    )
    mock_cliente_repository.exists_by_cpf_cnpj.return_value = True

    use_case = CreateClienteUseCase(mock_cliente_repository, mock_user_repository)
    command = CreateClienteCommand(
        nome="Maria Souza", usuario_id=1, cpf_cnpj="52998224725"
    )

    with pytest.raises(ValueError, match="Já existe um cliente"):
        await use_case.execute(command)

    mock_cliente_repository.save.assert_not_called()
