from datetime import UTC, datetime, timedelta

import pytest
from jose import JWTError, jwt

from infrastructure.config.config import settings
from infrastructure.config.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_gera_valor_diferente_da_senha_original():
    hashed = hash_password("minha-senha-secreta")

    assert hashed != "minha-senha-secreta"


def test_verify_password_aceita_senha_correta():
    hashed = hash_password("minha-senha-secreta")

    assert verify_password("minha-senha-secreta", hashed) is True


def test_verify_password_rejeita_senha_incorreta():
    hashed = hash_password("minha-senha-secreta")

    assert verify_password("senha-errada", hashed) is False


def test_create_access_token_gera_jwt_valido_com_claims():
    token = create_access_token({"sub": "1", "email": "user@example.com"})

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert payload["sub"] == "1"
    assert payload["email"] == "user@example.com"
    assert "exp" in payload


def test_decode_access_token_aceita_token_valido():
    token = create_access_token({"sub": "1", "email": "user@example.com"})

    payload = decode_access_token(token)

    assert payload["sub"] == "1"
    assert payload["email"] == "user@example.com"


def test_decode_access_token_rejeita_token_com_assinatura_invalida():
    token = jwt.encode(
        {"sub": "1", "exp": datetime.now(UTC) + timedelta(minutes=5)},
        "chave-errada",
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(JWTError):
        decode_access_token(token)


def test_decode_access_token_rejeita_token_expirado():
    token = jwt.encode(
        {"sub": "1", "exp": datetime.now(UTC) - timedelta(minutes=1)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(JWTError):
        decode_access_token(token)
