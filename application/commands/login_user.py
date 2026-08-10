from dataclasses import dataclass

from domain.repositories.user_repository import UserRepository
from infrastructure.auth.password_hasher import PasswordHasher
from infrastructure.config.security import create_access_token


@dataclass
class LoginUserCommand:
    """Comando para autenticação de usuário."""

    email: str
    password: str


class LoginUserUseCase:
    """Caso de uso para autenticação de usuários."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    async def execute(self, command: LoginUserCommand) -> str:
        user = await self.user_repository.find_by_email(command.email)

        if user is None:
            raise ValueError("Email ou senha inválidos.")

        if not self.password_hasher.verify(command.password, user.hashed_password):
            raise ValueError("Email ou senha inválidos.")

        token = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email,
            }
        )

        return token
