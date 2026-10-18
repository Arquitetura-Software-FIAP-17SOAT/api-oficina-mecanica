from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    """Porta para geração e validação de senhas."""

    @abstractmethod
    def hash(self, password: str) -> str:
        pass

    @abstractmethod
    def verify(self, password: str, hashed_password: str) -> bool:
        pass
