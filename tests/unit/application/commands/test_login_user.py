import pytest
from unittest.mock import AsyncMock, Mock

from application.commands.login_user import LoginUserCommand, LoginUserUseCase
from domain.entities.usuario import Usuario


@pytest.mark.asyncio
async def test_successful_login_returns_access_token():
    """Testa o login com credenciais válidas."""

    mock_repository = AsyncMock()
    user = Usuario(
        name="João Silva",
        email="test@example.com",
        hashed_password="hashed_password",
    )
    mock_repository.find_by_email.return_value = user

    mock_hasher = Mock()
    mock_hasher.verify.return_value = True

    use_case = LoginUserUseCase(mock_repository, mock_hasher)

    command = LoginUserCommand(email="test@example.com", password="password123")

    token = await use_case.execute(command)

    assert isinstance(token, str)
    assert token
    mock_repository.find_by_email.assert_awaited_once_with("test@example.com")
    mock_hasher.verify.assert_called_once_with("password123", "hashed_password")


@pytest.mark.asyncio
async def test_login_fails_for_invalid_credentials():
    """Testa o login com senha inválida."""

    mock_repository = AsyncMock()
    user = Usuario(
        name="João Silva",
        email="test@example.com",
        hashed_password="hashed_password",
    )
    mock_repository.find_by_email.return_value = user

    mock_hasher = Mock()
    mock_hasher.verify.return_value = False

    use_case = LoginUserUseCase(mock_repository, mock_hasher)

    command = LoginUserCommand(email="test@example.com", password="wrong-password")

    with pytest.raises(ValueError, match="Email ou senha inválidos."):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_login_fails_when_user_does_not_exist():
    """Testa o login com e-mail não cadastrado."""

    mock_repository = AsyncMock()
    mock_repository.find_by_email.return_value = None

    mock_hasher = Mock()

    use_case = LoginUserUseCase(mock_repository, mock_hasher)

    command = LoginUserCommand(email="nao-existe@example.com", password="qualquer")

    with pytest.raises(ValueError, match="Email ou senha inválidos."):
        await use_case.execute(command)

    mock_hasher.verify.assert_not_called()
