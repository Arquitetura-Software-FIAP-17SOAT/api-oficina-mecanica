import pytest

from domain.entities.usuario import Usuario


def test_create_valid_user():
    user = Usuario(
        name="Nilson",
        email="test@example.com",
        hashed_password="hashed_password",
    )

    assert user.name == "Nilson"
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_password"


def test_name_is_required():
    with pytest.raises(ValueError):
        Usuario(
            name="",
            email="test@example.com",
            hashed_password="hashed_password",
        )


def test_email_is_required():
    with pytest.raises(ValueError):
        Usuario(
            name="Nilson",
            email="",
            hashed_password="hashed_password",
        )


def test_password_is_required():
    with pytest.raises(ValueError):
        Usuario(
            name="Nilson",
            email="test@example.com",
            hashed_password="",
        )


def test_change_name():
    user = Usuario(
        name="Nilson", email="test@example.com", hashed_password="hash"
    )

    user.change_name("Nilson Silva")
    assert user.name == "Nilson Silva"

    with pytest.raises(ValueError):
        user.change_name("")


def test_change_email():
    user = Usuario(
        name="Nilson", email="test@example.com", hashed_password="hash"
    )

    user.change_email("Novo@Example.com")
    assert user.email == "novo@example.com"

    with pytest.raises(ValueError):
        user.change_email("")


def test_change_password():
    user = Usuario(
        name="Nilson", email="test@example.com", hashed_password="hash"
    )

    user.change_password("nova-hash")
    assert user.hashed_password == "nova-hash"

    with pytest.raises(ValueError):
        user.change_password("")