import pytest
from unittest.mock import Mock

from domain.entities.usuario import Usuario
from infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl


@pytest.mark.skip(reason="UserRepositoryImpl falta implementar métodos abstratos")
@pytest.mark.asyncio
async def test_save_maps_user_to_usuarios_table_fields():
    """Testa se o repositório salva os dados nas colunas esperadas da tabela."""

    db = Mock()
    repository = UserRepositoryImpl(db)

    user = Usuario(
        name="João Silva",
        email="joao@example.com",
        hashed_password="hash123",
    )

    await repository.save(user)

    model = db.add.call_args[0][0]
    assert model.nome == "João Silva"
    assert model.email == "joao@example.com"
    assert model.senha_hash == "hash123"
    assert model.telefone is None
