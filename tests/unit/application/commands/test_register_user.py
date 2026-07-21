import pytest
from unittest.mock import AsyncMock, Mock

from application.commands.register_user import (
    RegisterUserCommand,
    RegisterUserUseCase,
)


@pytest.mark.asyncio
async def test_successful_registration():
    """Testa o cadastro de um usuário com sucesso."""

    # Arrange
    mock_repository = AsyncMock()
    mock_repository.exists_by_email.return_value = False
    mock_repository.save.return_value = None

    mock_hasher = Mock()
    mock_hasher.hash.return_value = "hashed_password"

    use_case = RegisterUserUseCase(mock_repository, mock_hasher)

    command = RegisterUserCommand(
        name="João Silva",
        email="test@example.com",
        password="password123",
    )

    # Act
    user = await use_case.execute(command)

    # Assert
    assert user is not None
    assert user.name == "João Silva"
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_password"

    mock_repository.exists_by_email.assert_awaited_once_with(
        "test@example.com"
    )
    mock_repository.save.assert_awaited_once()
    mock_hasher.hash.assert_called_once_with("password123")


@pytest.mark.asyncio
async def test_registration_fails_if_email_exists():
    """Testa a tentativa de cadastrar um e-mail já existente."""

    # Arrange
    mock_repository = AsyncMock()
    mock_repository.exists_by_email.return_value = True

    mock_hasher = Mock()

    use_case = RegisterUserUseCase(mock_repository, mock_hasher)

    command = RegisterUserCommand(
        name="João Silva",
        email="test@example.com",
        password="password123",
    )

    # Act / Assert
    with pytest.raises(ValueError, match="E-mail já cadastrado."):
        await use_case.execute(command)

    mock_repository.save.assert_not_called()
    mock_hasher.hash.assert_not_called()