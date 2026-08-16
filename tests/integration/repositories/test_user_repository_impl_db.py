import pytest

from domain.entities.usuario import Usuario
from infrastructure.database.repositories.user_repository_impl import (
    UserRepositoryImpl,
)


@pytest.mark.asyncio
async def test_save_e_find_by_email(db_session):
    repository = UserRepositoryImpl(db_session)
    usuario = Usuario(
        name="João Silva", email="joao@example.com", hashed_password="hash123"
    )

    salvo = await repository.save(usuario)
    assert salvo.id is not None

    encontrado = await repository.find_by_email("joao@example.com")
    assert encontrado.name == "João Silva"


@pytest.mark.asyncio
async def test_find_by_email_retorna_none_quando_nao_existe(db_session):
    repository = UserRepositoryImpl(db_session)

    assert await repository.find_by_email("nao-existe@example.com") is None


@pytest.mark.asyncio
async def test_exists_by_email(db_session):
    repository = UserRepositoryImpl(db_session)
    await repository.save(
        Usuario(name="João Silva", email="joao@example.com", hashed_password="hash")
    )

    assert await repository.exists_by_email("joao@example.com") is True
    assert await repository.exists_by_email("outro@example.com") is False


@pytest.mark.asyncio
async def test_find_by_id(db_session):
    repository = UserRepositoryImpl(db_session)
    salvo = await repository.save(
        Usuario(name="João Silva", email="joao@example.com", hashed_password="hash")
    )

    encontrado = await repository.find_by_id(salvo.id)
    assert encontrado.email == "joao@example.com"
    assert await repository.find_by_id(999) is None


@pytest.mark.asyncio
async def test_list_update_delete_nao_estao_implementados(db_session):
    repository = UserRepositoryImpl(db_session)

    with pytest.raises(NotImplementedError):
        await repository.list()

    with pytest.raises(NotImplementedError):
        await repository.update(None)

    with pytest.raises(NotImplementedError):
        await repository.delete(1)
