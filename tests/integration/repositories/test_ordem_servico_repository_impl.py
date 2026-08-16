import pytest
from sqlalchemy.exc import IntegrityError

from domain.entities.ordem_servico import OrdemServico
from infrastructure.database.repositories.ordem_servico_repository_impl import (
    OrdemServicoRepositoryImpl,
)
from tests.integration.conftest import (
    criar_cliente,
    criar_marca,
    criar_servico,
    criar_usuario,
    criar_veiculo,
    seed_status_ordem_servico,
)


def _criar_veiculo(db_session):
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id)
    marca = criar_marca(db_session)
    return criar_veiculo(db_session, cliente.id, marca.id)


@pytest.mark.asyncio
async def test_save_cria_ordem_com_historico(db_session):
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)

    repository = OrdemServicoRepositoryImpl(db_session)
    ordem = OrdemServico(veiculo_id=str(veiculo.id), descricao="Revisão completa")

    salva = await repository.save(ordem)

    assert salva.id is not None

    encontrada = await repository.find_by_id(salva.id)
    assert encontrada.descricao is not None
    assert str(encontrada.descricao) == "Revisão completa"
    assert encontrada.status.value == "Recebida"
    assert len(encontrada.historico_status) == 1


@pytest.mark.asyncio
async def test_save_persiste_itens_e_atualiza_status(db_session):
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)
    servico = criar_servico(db_session)

    repository = OrdemServicoRepositoryImpl(db_session)
    ordem = OrdemServico(veiculo_id=str(veiculo.id), descricao="Revisão completa")
    ordem = await repository.save(ordem)

    ordem.iniciar_diagnostico()
    ordem.enviar_para_aprovacao(orcamento=200.0)
    ordem.adicionar_item(str(servico.id), 200.0)
    await repository.save(ordem)

    encontrada = await repository.find_by_id(ordem.id)
    assert encontrada.status.value == "Aguardando aprovação"
    assert len(encontrada.itens) == 1
    assert encontrada.itens[0]["servico_id"] == str(servico.id)
    assert len(encontrada.historico_status) == 3


@pytest.mark.asyncio
async def test_find_by_id_retorna_none_quando_nao_existe(db_session):
    repository = OrdemServicoRepositoryImpl(db_session)

    assert await repository.find_by_id(999) is None


@pytest.mark.asyncio
async def test_find_by_veiculo_id(db_session):
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)

    repository = OrdemServicoRepositoryImpl(db_session)
    await repository.save(
        OrdemServico(veiculo_id=str(veiculo.id), descricao="Revisão completa")
    )

    encontradas = await repository.find_by_veiculo_id(str(veiculo.id))
    assert len(encontradas) == 1


@pytest.mark.asyncio
async def test_find_by_status(db_session):
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)

    repository = OrdemServicoRepositoryImpl(db_session)
    await repository.save(
        OrdemServico(veiculo_id=str(veiculo.id), descricao="Revisão completa")
    )

    encontradas = await repository.find_by_status("Recebida")
    assert len(encontradas) == 1

    assert await repository.find_by_status("Entregue") == []


@pytest.mark.asyncio
async def test_list_all_pagina_resultados(db_session):
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)

    repository = OrdemServicoRepositoryImpl(db_session)
    for _ in range(3):
        await repository.save(
            OrdemServico(veiculo_id=str(veiculo.id), descricao="Revisão completa")
        )

    pagina = await repository.list_all(skip=0, limit=2)
    assert len(pagina) == 2


@pytest.mark.asyncio
async def test_delete_falha_quando_ha_historico_vinculado(db_session):
    """A ordem sempre nasce com um registro de histórico (linha 1 do fluxo),
    e a tabela de histórico não tem cascade nem permite FK nula — então a
    exclusão sempre esbarra em uma violação de integridade referencial."""
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)

    repository = OrdemServicoRepositoryImpl(db_session)
    ordem = await repository.save(
        OrdemServico(veiculo_id=str(veiculo.id), descricao="Revisão completa")
    )

    with pytest.raises(IntegrityError):
        await repository.delete(ordem.id)


@pytest.mark.asyncio
async def test_delete_retorna_false_quando_ordem_nao_existe(db_session):
    repository = OrdemServicoRepositoryImpl(db_session)

    assert await repository.delete(999) is False
