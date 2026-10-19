"""Falha parcial na API: OS e estoque não podem ficar inconsistentes."""

from sqlalchemy import select

from adapters.database.models import InsumoModel, OrdemServicoModel
from adapters.database.repositories.insumo_repository_impl import InsumoRepositoryImpl
from adapters.database.repositories.ordem_servico_repository_impl import (
    OrdemServicoRepositoryImpl,
)
from tests.integration.conftest import (
    criar_cliente,
    criar_insumo,
    criar_marca,
    criar_servico,
    criar_usuario,
    criar_veiculo,
    seed_status_ordem_servico,
)


def _total_ordens(db_session) -> int:
    db_session.expire_all()
    return len(db_session.scalars(select(OrdemServicoModel)).all())


def _veiculo(db_session):
    seed_status_ordem_servico(db_session)
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id)
    return criar_veiculo(db_session, cliente.id, criar_marca(db_session).id)


def test_abertura_de_os_nao_cria_a_os_se_a_baixa_de_estoque_falha(
    client, db_session, monkeypatch
):
    veiculo = _veiculo(db_session)
    servico = criar_servico(db_session)
    insumo = criar_insumo(db_session, estoque=10)

    async def update_que_falha(self, insumo):
        raise RuntimeError("banco caiu")

    monkeypatch.setattr(InsumoRepositoryImpl, "update", update_que_falha)

    resposta = client.post(
        "/ordens-servico",
        json={
            "veiculo_id": str(veiculo.id),
            "cliente_id": veiculo.cliente_id,
            "descricao": "Revisão completa",
            "servicos": [{"servico_id": str(servico.id)}],
            "insumos": [{"insumo_id": insumo.id, "quantidade": 3}],
        },
    )

    assert resposta.status_code == 500
    assert _total_ordens(db_session) == 0
    db_session.expire_all()
    assert db_session.get(InsumoModel, insumo.id).estoque == 10


def test_adicionar_insumo_nao_deixa_estoque_baixado_se_a_os_nao_grava(
    client, db_session, monkeypatch
):
    veiculo = _veiculo(db_session)
    insumo = criar_insumo(db_session, estoque=10)
    ordem_id = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "cliente_id": veiculo.cliente_id, "descricao": "Revisão completa"},
    ).json()["id"]

    async def save_que_falha(self, ordem_servico):
        raise RuntimeError("banco caiu")

    monkeypatch.setattr(OrdemServicoRepositoryImpl, "save", save_que_falha)

    resposta = client.post(
        f"/ordens-servico/{ordem_id}/adicionar-insumo",
        json={"insumo_id": insumo.id, "quantidade": 3},
    )

    assert resposta.status_code == 500
    db_session.expire_all()
    assert db_session.get(InsumoModel, insumo.id).estoque == 10
