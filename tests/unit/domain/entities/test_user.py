import pytest

from domain.entities.user import User


def test_create_valid_user():
    user = User(
        name="Nilson",
        email="test@example.com",
        hashed_password="hashed_password",
    )

    assert user.name == "Nilson"
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_password"


def test_name_is_required():
    with pytest.raises(ValueError):
        User(
            name="",
            email="test@example.com",
            hashed_password="hashed_password",
        )


def test_email_is_required():
    with pytest.raises(ValueError):
        User(
            name="Nilson",
            email="",
            hashed_password="hashed_password",
        )


def test_password_is_required():
    with pytest.raises(ValueError):
        User(
            name="Nilson",
            email="test@example.com",
            hashed_password="",
        )