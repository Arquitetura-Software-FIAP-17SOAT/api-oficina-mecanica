from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from application.ports.token_decoder import TokenDecoder, TokenInvalidoError
from presentation.dependencies.dependencies import get_token_decoder

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

CREDENCIAIS_INVALIDAS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais inválidas ou token expirado.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    token_decoder: TokenDecoder = Depends(get_token_decoder),
) -> dict:
    """Valida o token JWT enviado no header ``Authorization: Bearer <token>``.

    A validação fica atrás da porta ``TokenDecoder``; aqui só se traduz o
    resultado para HTTP. Devolve as claims (``sub``, ``email``, ``exp``) para
    uso nos endpoints protegidos.
    """

    try:
        payload = token_decoder.decode(token)
    except TokenInvalidoError:
        raise CREDENCIAIS_INVALIDAS

    if payload.get("sub") is None:
        raise CREDENCIAIS_INVALIDAS

    return payload
