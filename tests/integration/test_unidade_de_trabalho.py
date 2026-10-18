"""A unidade de trabalho torna várias escritas de repositórios atômicas."""

import asyncio

import pytest
from sqlalchemy import select

from adapters.database.models import InsumoModel, OrdemServicoModel
from adapters.database.repositories.insumo_repository_impl import InsumoRepositoryImpl
from adapters.database.transaction import SqlAlchemyUnitOfWork
from domain.entities.ordem_servico import OrdemServico
from tests.integration.conftest import (
    criar_cliente,
    criar_insumo,
    criar_marca,
    criar_servico,
    criar_usuario,
    criar_veiculo,
    seed_status_ordem_servico,
)
from adapters.database.repositories.ordem_servico_repository_impl import (
    OrdemServicoRepositoryImpl,
)


def _total_ordens(db_session) -> int:
    db_session.expire_all()
    return len(db_session.scalars(select(OrdemServicoModel)).all())


def _veiculo(db_session):
    seed_status_ordem_servico(db_session)
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id)
    return criar_veiculo(db_session, cliente.id, criar_marca(db_session).id)


def test_confirma_as_escritas_juntas_ao_final_do_bloco(db_session):
    veiculo = _veiculo(db_session)
    ordens = OrdemServicoRepositoryImpl(db_session)

    async def fluxo():
        async with SqlAlchemyUnitOfWork(db_session):
            await ordens.save(OrdemServico(veiculo_id=str(veiculo.id), descricao="Revisão"))
            # dentro do bloco nada foi confirmado ainda
            assert db_session.in_transaction()

    asyncio.run(fluxo())

    assert _total_ordens(db_session) == 1


def test_desfaz_todas_as_escritas_quando_o_bloco_falha(db_session):
    veiculo = _veiculo(db_session)
    insumo = criar_insumo(db_session, estoque=10)
    ordens = OrdemServicoRepositoryImpl(db_session)
    insumos = InsumoRepositoryImpl(db_session)

    async def fluxo():
        async with SqlAlchemyUnitOfWork(db_session):
            await ordens.save(OrdemServico(veiculo_id=str(veiculo.id), descricao="Revisão"))
            entidade = await insumos.find_by_id(insumo.id)
            entidade.remover_estoque(4)
            await insumos.update(entidade)
            raise RuntimeError("falha no meio")

    with pytest.raises(RuntimeError):
        asyncio.run(fluxo())

    assert _total_ordens(db_session) == 0
    db_session.expire_all()
    assert db_session.get(InsumoModel, insumo.id).estoque == 10


def test_fora_da_unidade_de_trabalho_cada_escrita_e_confirmada_na_hora(db_session):
    veiculo = _veiculo(db_session)
    ordens = OrdemServicoRepositoryImpl(db_session)

    asyncio.run(ordens.save(OrdemServico(veiculo_id=str(veiculo.id), descricao="Revisão")))
    db_session.rollback()  # um rollback depois não pode desfazer o que foi salvo

    assert _total_ordens(db_session) == 1


def test_marcador_de_transacao_e_removido_apos_o_bloco(db_session):
    _veiculo(db_session)

    async def falha():
        async with SqlAlchemyUnitOfWork(db_session):
            raise ValueError("x")

    with pytest.raises(ValueError):
        asyncio.run(falha())

    assert not db_session.info
