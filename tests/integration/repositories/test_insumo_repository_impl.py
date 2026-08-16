from decimal import Decimal

import pytest

from domain.entities.insumo import Insumo
from infrastructure.database.repositories.insumo_repository_impl import (
    InsumoRepositoryImpl,
)
from tests.integration.conftest import criar_insumo, criar_servico


@pytest.mark.asyncio
async def test_save_e_find_by_id(db_session):
    repository = InsumoRepositoryImpl(db_session)

    insumo = Insumo(nome="Óleo 5W30", preco_unitario=Decimal("45.90"), estoque=10)
    salvo = await repository.save(insumo)

    assert salvo.id is not None

    encontrado = await repository.find_by_id(salvo.id)
    assert encontrado.nome == "Óleo 5W30"
    assert encontrado.estoque == 10


@pytest.mark.asyncio
async def test_find_by_id_retorna_none_quando_nao_existe(db_session):
    repository = InsumoRepositoryImpl(db_session)

    assert await repository.find_by_id(999) is None


@pytest.mark.asyncio
async def test_list_retorna_em_ordem_alfabetica(db_session):
    criar_insumo(db_session, nome="Filtro de óleo")
    criar_insumo(db_session, nome="Amortecedor")

    repository = InsumoRepositoryImpl(db_session)
    insumos = await repository.list()

    assert [i.nome for i in insumos] == ["Amortecedor", "Filtro de óleo"]


@pytest.mark.asyncio
async def test_list_estoque_baixo(db_session):
    criar_insumo(db_session, nome="Óleo", estoque=1, quantidade_minima=5)
    criar_insumo(db_session, nome="Filtro", estoque=10, quantidade_minima=2)

    repository = InsumoRepositoryImpl(db_session)
    insumos = await repository.list_estoque_baixo()

    assert [i.nome for i in insumos] == ["Óleo"]


@pytest.mark.asyncio
async def test_update_altera_dados_persistidos(db_session):
    model = criar_insumo(db_session, nome="Óleo", estoque=10)

    repository = InsumoRepositoryImpl(db_session)
    insumo = await repository.find_by_id(model.id)
    insumo.change_nome("Óleo sintético")
    insumo.adicionar_estoque(5)

    await repository.update(insumo)

    atualizado = await repository.find_by_id(model.id)
    assert atualizado.nome == "Óleo sintético"
    assert atualizado.estoque == 15


@pytest.mark.asyncio
async def test_update_falha_quando_insumo_nao_existe(db_session):
    repository = InsumoRepositoryImpl(db_session)
    insumo = Insumo(id=999, nome="Fantasma")

    with pytest.raises(ValueError, match="não encontrado"):
        await repository.update(insumo)


@pytest.mark.asyncio
async def test_delete_remove_insumo(db_session):
    model = criar_insumo(db_session)

    repository = InsumoRepositoryImpl(db_session)
    await repository.delete(model.id)

    assert await repository.find_by_id(model.id) is None


@pytest.mark.asyncio
async def test_delete_e_silencioso_quando_insumo_nao_existe(db_session):
    repository = InsumoRepositoryImpl(db_session)

    await repository.delete(999)


@pytest.mark.asyncio
async def test_exists_by_nome_e_case_insensitive(db_session):
    criar_insumo(db_session, nome="Filtro de Combustivel")

    repository = InsumoRepositoryImpl(db_session)

    assert await repository.exists_by_nome("filtro de combustivel") is True
    assert await repository.exists_by_nome("Amortecedor") is False


@pytest.mark.asyncio
async def test_has_vinculos(db_session):
    insumo = criar_insumo(db_session)
    servico = criar_servico(db_session)

    repository = InsumoRepositoryImpl(db_session)
    assert await repository.has_vinculos(insumo.id) is False

    from infrastructure.database.models import ServicoInsumoModel

    db_session.add(
        ServicoInsumoModel(servico_id=servico.id, insumo_id=insumo.id, quantidade=1)
    )
    db_session.commit()

    assert await repository.has_vinculos(insumo.id) is True
