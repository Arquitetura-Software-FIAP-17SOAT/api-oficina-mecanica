from abc import ABC, abstractmethod

from passlib.context import CryptContext


class PasswordHasher(ABC):
    """Interface para geração e validação de senhas."""

    @abstractmethod
    def hash(self, password: str) -> str:
        pass

    @abstractmethod
    def verify(self, password: str, hashed_password: str) -> bool:
        pass


class BCryptPasswordHasher(PasswordHasher):
    """Implementação utilizando BCrypt."""

    def __init__(self):
        self._pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
        )

    def hash(self, password: str) -> str:
        return self._pwd_context.hash(password)

    def verify(self, password: str, hashed_password: str) -> bool:
        return self._pwd_context.verify(password, hashed_password)