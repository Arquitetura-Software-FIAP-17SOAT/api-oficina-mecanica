from jose import JWTError

from adapters.config.security import decode_access_token
from application.ports.token_decoder import TokenDecoder, TokenInvalidoError


class JWTTokenDecoder(TokenDecoder):
    """Implementação utilizando JWT."""

    def decode(self, token: str) -> dict:
        try:
            return decode_access_token(token)
        except JWTError as e:
            raise TokenInvalidoError(str(e)) from e
