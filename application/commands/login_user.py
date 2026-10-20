from dataclasses import dataclass

from domain.repositories.user_repository import UserRepository
from application.ports.password_hasher import PasswordHasher
from application.ports.token_generator import TokenGenerator


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
        token_generator: TokenGenerator,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_generator = token_generator

    async def execute(self, command: LoginUserCommand) -> str:
        user = await self.user_repository.find_by_email(command.email)

        if user is None:
            raise ValueError("Email ou senha inválidos.")

        if not self.password_hasher.verify(command.password, user.hashed_password):
            raise ValueError("Email ou senha inválidos.")

        token = self.token_generator.generate(
            {
                "sub": str(user.id),
                "email": user.email,
            }
        )

        return token
