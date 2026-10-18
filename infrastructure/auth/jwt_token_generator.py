from application.ports.token_generator import TokenGenerator
from infrastructure.config.security import create_access_token


class JWTTokenGenerator(TokenGenerator):
    """Implementação utilizando JWT."""

    def generate(self, claims: dict) -> str:
        return create_access_token(claims)
