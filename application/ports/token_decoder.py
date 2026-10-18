from abc import ABC, abstractmethod


class TokenInvalidoError(Exception):
    """Token sem validade: malformado, expirado ou com assinatura inválida."""


class TokenDecoder(ABC):
    """Porta para validar um token de acesso e ler suas claims."""

    @abstractmethod
    def decode(self, token: str) -> dict:
        """Devolve as claims do token ou levanta ``TokenInvalidoError``."""
