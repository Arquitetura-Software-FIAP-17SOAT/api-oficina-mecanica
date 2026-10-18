from abc import ABC, abstractmethod


class TokenGenerator(ABC):
    """Porta para emissão de tokens de acesso."""

    @abstractmethod
    def generate(self, claims: dict) -> str:
        pass
