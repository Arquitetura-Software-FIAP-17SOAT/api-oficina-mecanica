from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException
from jose import jwt

from adapters.config.config import settings
from adapters.auth.jwt_token_decoder import JWTTokenDecoder
from adapters.config.security import create_access_token
from presentation.dependencies.auth_dependencies import get_current_user

DECODER = JWTTokenDecoder()


def test_get_current_user_com_token_valido():
    token = create_access_token({"sub": "1", "email": "user@example.com"})

    payload = get_current_user(token, DECODER)

    assert payload["sub"] == "1"
    assert payload["email"] == "user@example.com"


def test_get_current_user_com_token_invalido():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user("token-invalido", DECODER)

    assert exc_info.value.status_code == 401


def test_get_current_user_com_token_expirado():
    token = jwt.encode(
        {"sub": "1", "exp": datetime.now(UTC) - timedelta(minutes=1)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token, DECODER)

    assert exc_info.value.status_code == 401


def test_get_current_user_sem_claim_sub():
    token = jwt.encode(
        {"email": "user@example.com", "exp": datetime.now(UTC) + timedelta(minutes=5)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token, DECODER)

    assert exc_info.value.status_code == 401
