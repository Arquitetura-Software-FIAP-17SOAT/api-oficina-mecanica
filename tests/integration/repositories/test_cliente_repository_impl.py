import pytest

from domain.entities.cliente import Cliente
from infrastructure.database.repositories.cliente_repository_impl import (
    ClienteRepositoryImpl,
)
from tests.integration.conftest import (
    criar_cliente,
    criar_marca,
    criar_usuario,
    criar_veiculo,
)


@pytest.mark.asyncio
async def test_save_e_find_by_id(db_session):
    usuario = criar_usuario(db_session)
    repository = ClienteRepositoryImpl(db_session)

    cliente = Cliente(nome="Maria Souza", usuario_id=usuario.id, cpf_cnpj="52998224725")
    salvo = await repository.save(cliente)

    assert salvo.id is not None

    encontrado = await repository.find_by_id(salvo.id)
    assert encontrado.nome == "Maria Souza"
    assert str(encontrado.cpf_cnpj) == "52998224725"


@pytest.mark.asyncio
async def test_find_by_id_retorna_none_quando_nao_existe(db_session):
    repository = ClienteRepositoryImpl(db_session)

    assert await repository.find_by_id(999) is None


@pytest.mark.asyncio
async def test_list_retorna_em_ordem_alfabetica(db_session):
    usuario = criar_usuario(db_session)
    criar_cliente(db_session, usuario.id, nome="Zeca")
    criar_cliente(db_session, usuario.id, nome="Ana")

    repository = ClienteRepositoryImpl(db_session)
    clientes = await repository.list()

    assert [c.nome for c in clientes] == ["Ana", "Zeca"]


@pytest.mark.asyncio
async def test_update_altera_dados_persistidos(db_session):
    usuario = criar_usuario(db_session)
    model = criar_cliente(db_session, usuario.id, nome="Maria")

    repository = ClienteRepositoryImpl(db_session)
    cliente = await repository.find_by_id(model.id)
    cliente.change_nome("Maria Souza Lima")

    await repository.update(cliente)

    atualizado = await repository.find_by_id(model.id)
    assert atualizado.nome == "Maria Souza Lima"


@pytest.mark.asyncio
async def test_update_falha_quando_cliente_nao_existe(db_session):
    repository = ClienteRepositoryImpl(db_session)
    cliente = Cliente(id=999, nome="Fantasma", usuario_id=1)

    with pytest.raises(ValueError, match="não encontrado"):
        await repository.update(cliente)


@pytest.mark.asyncio
async def test_delete_remove_cliente(db_session):
    usuario = criar_usuario(db_session)
    model = criar_cliente(db_session, usuario.id)

    repository = ClienteRepositoryImpl(db_session)
    await repository.delete(model.id)

    assert await repository.find_by_id(model.id) is None


@pytest.mark.asyncio
async def test_delete_e_silencioso_quando_cliente_nao_existe(db_session):
    repository = ClienteRepositoryImpl(db_session)

    await repository.delete(999)


@pytest.mark.asyncio
async def test_exists_by_cpf_cnpj(db_session):
    usuario = criar_usuario(db_session)
    criar_cliente(db_session, usuario.id, cpf_cnpj="52998224725")

    repository = ClienteRepositoryImpl(db_session)

    assert await repository.exists_by_cpf_cnpj("52998224725") is True
    assert await repository.exists_by_cpf_cnpj("11144477735") is False


@pytest.mark.asyncio
async def test_has_veiculos(db_session):
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id)
    marca = criar_marca(db_session)

    repository = ClienteRepositoryImpl(db_session)
    assert await repository.has_veiculos(cliente.id) is False

    criar_veiculo(db_session, cliente.id, marca.id)
    assert await repository.has_veiculos(cliente.id) is True
