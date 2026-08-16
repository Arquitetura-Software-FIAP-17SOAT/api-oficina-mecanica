from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from infrastructure.config.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

CREDENCIAIS_INVALIDAS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais inválidas ou token expirado.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Valida o token JWT enviado no header ``Authorization: Bearer <token>``.

    Reaproveita o mesmo par segredo/algoritmo usado por
    ``create_access_token`` (login) para decodificar o token, e devolve o
    payload (``sub``, ``email``, ``exp``) para uso nos endpoints protegidos.
    """

    try:
        payload = decode_access_token(token)
    except JWTError:
        raise CREDENCIAIS_INVALIDAS

    if payload.get("sub") is None:
        raise CREDENCIAIS_INVALIDAS

    return payload
