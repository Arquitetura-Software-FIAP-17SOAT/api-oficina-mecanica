from jose import jwt

from infrastructure.config.config import settings
from infrastructure.config.security import (
    create_access_token,
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
