from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from adapters.auth.jwt_token_decoder import JWTTokenDecoder
from adapters.config.config import settings
from adapters.config.security import create_access_token
from application.ports.token_decoder import TokenInvalidoError


def test_decodifica_token_valido():
    token = create_access_token({"sub": "1", "email": "user@example.com"})

    claims = JWTTokenDecoder().decode(token)

    assert claims["sub"] == "1"
    assert claims["email"] == "user@example.com"


def test_token_malformado_vira_token_invalido():
    with pytest.raises(TokenInvalidoError):
        JWTTokenDecoder().decode("token-invalido")


def test_token_expirado_vira_token_invalido():
    token = jwt.encode(
        {"sub": "1", "exp": datetime.now(UTC) - timedelta(minutes=1)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(TokenInvalidoError):
        JWTTokenDecoder().decode(token)


def test_assinatura_invalida_vira_token_invalido():
    token = jwt.encode(
        {"sub": "1", "exp": datetime.now(UTC) + timedelta(minutes=5)},
        "outra-chave",
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(TokenInvalidoError):
        JWTTokenDecoder().decode(token)
