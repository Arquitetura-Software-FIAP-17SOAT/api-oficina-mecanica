import pytest

from domain.entities.veiculo import Veiculo
from infrastructure.database.repositories.veiculo_repository_impl import (
    VeiculoRepositoryImpl,
)
from tests.integration.conftest import criar_cliente, criar_marca, criar_usuario, criar_veiculo


@pytest.mark.asyncio
async def test_save_e_find_by_id(db_session):
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id)
    marca = criar_marca(db_session)

    repository = VeiculoRepositoryImpl(db_session)
    veiculo = Veiculo(
        cliente_id=cliente.id, marca_id=marca.id, placa="ABC1D23", modelo="Gol 1.0"
    )
    salvo = await repository.save(veiculo)

    assert salvo.id is not None
    assert salvo.criado_em is not None

    encontrado = await repository.find_by_id(salvo.id)
    assert str(encontrado.placa) == "ABC1D23"


@pytest.mark.asyncio
async def test_find_by_id_retorna_none_quando_nao_existe(db_session):
    repository = VeiculoRepositoryImpl(db_session)

    assert await repository.find_by_id(999) is None


@pytest.mark.asyncio
async def test_list_ordena_por_placa_e_filtra_por_cliente(db_session):
    usuario = criar_usuario(db_session)
    cliente1 = criar_cliente(db_session, usuario.id, nome="Cliente 1")
    cliente2 = criar_cliente(db_session, usuario.id, nome="Cliente 2")
    marca = criar_marca(db_session)

    criar_veiculo(db_session, cliente1.id, marca.id, placa="ZZZ9999")
    criar_veiculo(db_session, cliente1.id, marca.id, placa="AAA1111")
    criar_veiculo(db_session, cliente2.id, marca.id, placa="BBB2222")

    repository = VeiculoRepositoryImpl(db_session)

    todos = await repository.list()
    assert [v.placa.value for v in todos] == ["AAA1111", "BBB2222", "ZZZ9999"]

    do_cliente1 = await repository.list(cliente_id=cliente1.id)
    assert [v.placa.value for v in do_cliente1] == ["AAA1111", "ZZZ9999"]


@pytest.mark.asyncio
async def test_update_altera_dados_persistidos(db_session):
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id)
    marca = criar_marca(db_session)
    model = criar_veiculo(db_session, cliente.id, marca.id, modelo="Gol")

    repository = VeiculoRepositoryImpl(db_session)
    veiculo = await repository.find_by_id(model.id)
    veiculo.change_modelo("Gol 1.6")

    await repository.update(veiculo)

    atualizado = await repository.find_by_id(model.id)
    assert atualizado.modelo == "Gol 1.6"


@pytest.mark.asyncio
async def test_update_falha_quando_veiculo_nao_existe(db_session):
    repository = VeiculoRepositoryImpl(db_session)
    veiculo = Veiculo(
        id=999, cliente_id=1, marca_id=1, placa="ABC1D23", modelo="Fantasma"
    )

    with pytest.raises(ValueError, match="não encontrado"):
        await repository.update(veiculo)


@pytest.mark.asyncio
async def test_delete_remove_veiculo(db_session):
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id)
    marca = criar_marca(db_session)
    model = criar_veiculo(db_session, cliente.id, marca.id)

    repository = VeiculoRepositoryImpl(db_session)
    await repository.delete(model.id)

    assert await repository.find_by_id(model.id) is None


@pytest.mark.asyncio
async def test_exists_by_placa(db_session):
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id)
    marca = criar_marca(db_session)
    criar_veiculo(db_session, cliente.id, marca.id, placa="ABC1D23")

    repository = VeiculoRepositoryImpl(db_session)

    assert await repository.exists_by_placa("ABC1D23") is True
    assert await repository.exists_by_placa("XYZ9999") is False


@pytest.mark.asyncio
async def test_marca_exists(db_session):
    marca = criar_marca(db_session)

    repository = VeiculoRepositoryImpl(db_session)

    assert await repository.marca_exists(marca.id) is True
    assert await repository.marca_exists(999) is False


@pytest.mark.asyncio
async def test_has_ordens_servico(db_session):
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id)
    marca = criar_marca(db_session)
    veiculo = criar_veiculo(db_session, cliente.id, marca.id)

    repository = VeiculoRepositoryImpl(db_session)
    assert await repository.has_ordens_servico(veiculo.id) is False

    from infrastructure.database.models import OrdemServicoModel

    db_session.add(
        OrdemServicoModel(
            veiculo_id=veiculo.id, descricao="Manutenção", status="Recebida"
        )
    )
    db_session.commit()

    assert await repository.has_ordens_servico(veiculo.id) is True
