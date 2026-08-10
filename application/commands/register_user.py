from dataclasses import dataclass

from domain.entities.usuario import Usuario
from domain.repositories.user_repository import UserRepository
from infrastructure.auth.password_hasher import PasswordHasher


@dataclass
class RegisterUserCommand:
    """Comando para cadastro de usuário."""

    name: str
    email: str
    password: str


class RegisterUserUseCase:
    """Caso de uso para cadastro de usuários."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    async def execute(self, command: RegisterUserCommand) -> Usuario:
        # Verifica se o e-mail já está cadastrado
        if await self.user_repository.exists_by_email(command.email):
            raise ValueError("E-mail já cadastrado.")

        # Gera o hash da senha
        hashed_password = self.password_hasher.hash(command.password)

        # Cria a entidade
        user = Usuario(
            name=command.name,
            email=command.email,
            hashed_password=hashed_password,
        )

        # Persiste
        await self.user_repository.save(user)

        return user