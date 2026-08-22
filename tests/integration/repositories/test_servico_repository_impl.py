from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from domain.entities.servico import Servico
from infrastructure.database.models import (
    OrdemServicoModel,
    OrdemServicoServicoModel,
    ServicoInsumoModel,
)
from infrastructure.database.repositories.servico_repository_impl import (
    ServicoRepositoryImpl,
)
from tests.integration.conftest import (
    criar_cliente,
    criar_insumo,
    criar_marca,
    criar_servico,
    criar_usuario,
    criar_veiculo,
)


@pytest.mark.asyncio
async def test_save_e_find_by_id(db_session):
    repository = ServicoRepositoryImpl(db_session)

    servico = Servico(nome="Troca de óleo", valor=Decimal("120.00"))
    salvo = await repository.save(servico)

    assert salvo.id is not None

    encontrado = await repository.find_by_id(salvo.id)
    assert encontrado.nome == "Troca de óleo"
    assert encontrado.valor.value == Decimal("120.00")


@pytest.mark.asyncio
async def test_find_by_id_retorna_none_quando_nao_existe(db_session):
    repository = ServicoRepositoryImpl(db_session)

    assert await repository.find_by_id(999) is None


@pytest.mark.asyncio
async def test_list_retorna_em_ordem_alfabetica(db_session):
    criar_servico(db_session, nome="Troca de óleo")
    criar_servico(db_session, nome="Alinhamento")

    repository = ServicoRepositoryImpl(db_session)
    servicos = await repository.list()

    assert [s.nome for s in servicos] == ["Alinhamento", "Troca de óleo"]


@pytest.mark.asyncio
async def test_update_altera_dados_persistidos(db_session):
    model = criar_servico(db_session, nome="Troca de óleo")

    repository = ServicoRepositoryImpl(db_session)
    servico = await repository.find_by_id(model.id)
    servico.change_valor(Decimal("150.00"))

    await repository.update(servico)

    atualizado = await repository.find_by_id(model.id)
    assert atualizado.valor.value == Decimal("150.00")


@pytest.mark.asyncio
async def test_update_falha_quando_servico_nao_existe(db_session):
    repository = ServicoRepositoryImpl(db_session)
    servico = Servico(id=999, nome="Fantasma", valor=Decimal("10.00"))

    with pytest.raises(ValueError, match="não encontrado"):
        await repository.update(servico)


@pytest.mark.asyncio
async def test_delete_remove_servico(db_session):
    model = criar_servico(db_session)

    repository = ServicoRepositoryImpl(db_session)
    await repository.delete(model.id)

    assert await repository.find_by_id(model.id) is None


@pytest.mark.asyncio
async def test_exists_by_nome_e_case_insensitive(db_session):
    criar_servico(db_session, nome="Alinhamento e Balanceamento")

    repository = ServicoRepositoryImpl(db_session)

    assert await repository.exists_by_nome("alinhamento e balanceamento") is True
    assert await repository.exists_by_nome("Revisão") is False


@pytest.mark.asyncio
async def test_has_vinculos_por_insumo(db_session):
    servico = criar_servico(db_session)
    insumo = criar_insumo(db_session)

    repository = ServicoRepositoryImpl(db_session)
    assert await repository.has_vinculos(servico.id) is False

    db_session.add(
        ServicoInsumoModel(servico_id=servico.id, insumo_id=insumo.id, quantidade=1)
    )
    db_session.commit()

    assert await repository.has_vinculos(servico.id) is True


@pytest.mark.asyncio
async def test_has_vinculos_por_ordem_servico(db_session):
    servico = criar_servico(db_session)
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id)
    marca = criar_marca(db_session)
    veiculo = criar_veiculo(db_session, cliente.id, marca.id)

    from infrastructure.database.models import OrdemServicoModel

    ordem = OrdemServicoModel(
        veiculo_id=veiculo.id, descricao="Manutenção", status="Recebida"
    )
    db_session.add(ordem)
    db_session.commit()
    db_session.refresh(ordem)

    repository = ServicoRepositoryImpl(db_session)
    assert await repository.has_vinculos(servico.id) is False

    db_session.add(
        OrdemServicoServicoModel(
            ordem_servico_id=ordem.id,
            servico_id=servico.id,
            valor=Decimal("100.00"),
            quantidade=1,
        )
    )
    db_session.commit()

    assert await repository.has_vinculos(servico.id) is True


@pytest.mark.asyncio
async def test_list_tempo_medio_execucao_ignora_execucoes_incompletas(db_session):
    servico = criar_servico(db_session)
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id)
    marca = criar_marca(db_session)
    veiculo = criar_veiculo(db_session, cliente.id, marca.id)

    primeira_ordem = OrdemServicoModel(
        veiculo_id=veiculo.id, descricao="Manutenção 1", status="Em execução"
    )
    segunda_ordem = OrdemServicoModel(
        veiculo_id=veiculo.id, descricao="Manutenção 2", status="Em execução"
    )
    db_session.add_all([primeira_ordem, segunda_ordem])
    db_session.commit()
    db_session.refresh(primeira_ordem)
    db_session.refresh(segunda_ordem)

    inicio = datetime(2025, 1, 15, 10, 0, 0)
    db_session.add_all(
        [
            OrdemServicoServicoModel(
                ordem_servico_id=primeira_ordem.id,
                servico_id=servico.id,
                valor=Decimal("120.00"),
                data_inicio=inicio,
                data_fim=inicio + timedelta(hours=2),
            ),
            OrdemServicoServicoModel(
                ordem_servico_id=segunda_ordem.id,
                servico_id=servico.id,
                valor=Decimal("120.00"),
                data_inicio=inicio,
            ),
        ]
    )
    db_session.commit()

    repository = ServicoRepositoryImpl(db_session)
    resultado = await repository.list_tempo_medio_execucao()

    assert resultado[0][0] == servico.id
    assert resultado[0][1] == servico.nome
    assert resultado[0][2] == pytest.approx(2.0)
    assert resultado[0][3] == 1
