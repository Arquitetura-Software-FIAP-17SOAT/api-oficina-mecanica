"""Notificação externa de aprovação/recusa do orçamento (autenticada por X-API-Key)."""

import pytest

from adapters.config.config import settings
from tests.integration.conftest import (
    criar_cliente,
    criar_marca,
    criar_servico,
    criar_usuario,
    criar_veiculo,
    seed_status_ordem_servico,
)

CHAVE = "chave-de-teste"
HEADERS = {"X-API-Key": CHAVE}


@pytest.fixture(autouse=True)
def chave_configurada(monkeypatch):
    monkeypatch.setattr(settings, "INTEGRACAO_API_KEY", CHAVE)


def _ordem_aguardando_aprovacao(client, db_session):
    seed_status_ordem_servico(db_session)
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id)
    veiculo = criar_veiculo(db_session, cliente.id, criar_marca(db_session).id)
    servico = criar_servico(db_session)

    ordem_id = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    ).json()["id"]
    client.post(f"/ordens-servico/{ordem_id}/iniciar-diagnostico", json={})
    client.post(
        f"/ordens-servico/{ordem_id}/adicionar-item",
        json={"servico_id": str(servico.id), "quantidade": 1},
    )
    client.post(f"/ordens-servico/{ordem_id}/enviar-aprovacao", json={})

    return ordem_id


def _notificar(cliente_http, ordem_id, decisao, headers=HEADERS):
    return cliente_http.post(
        f"/integracoes/ordens-servico/{ordem_id}/orcamento",
        json={"decisao": decisao},
        headers=headers,
    )


def test_aprovacao_externa_inicia_a_execucao(client, unauthenticated_client, db_session):
    ordem_id = _ordem_aguardando_aprovacao(client, db_session)

    resposta = _notificar(unauthenticated_client, ordem_id, "aprovado")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["ordem_servico_id"] == ordem_id
    assert corpo["status"] == "Em execução"
    assert corpo["status_orcamento"] == "Aprovado"


def test_recusa_externa_finaliza_a_os(client, unauthenticated_client, db_session):
    ordem_id = _ordem_aguardando_aprovacao(client, db_session)

    resposta = _notificar(unauthenticated_client, ordem_id, "recusado")

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "Finalizada"
    assert resposta.json()["status_orcamento"] == "Rejeitado"


def test_sem_chave_retorna_401(client, unauthenticated_client, db_session):
    ordem_id = _ordem_aguardando_aprovacao(client, db_session)

    resposta = _notificar(unauthenticated_client, ordem_id, "aprovado", headers={})

    assert resposta.status_code == 401


def test_chave_errada_retorna_401_e_nao_altera_a_os(
    client, unauthenticated_client, db_session
):
    ordem_id = _ordem_aguardando_aprovacao(client, db_session)

    resposta = _notificar(
        unauthenticated_client, ordem_id, "aprovado", headers={"X-API-Key": "outra"}
    )

    assert resposta.status_code == 401
    assert client.get(f"/ordens-servico/{ordem_id}").json()["status"] == (
        "Aguardando aprovação"
    )


def test_token_jwt_de_funcionario_nao_substitui_a_chave(
    client, unauthenticated_client, db_session
):
    ordem_id = _ordem_aguardando_aprovacao(client, db_session)

    resposta = _notificar(
        unauthenticated_client,
        ordem_id,
        "aprovado",
        headers={"Authorization": client.headers["Authorization"]},
    )

    assert resposta.status_code == 401


def test_integracao_desligada_sem_chave_configurada_retorna_503(
    client, unauthenticated_client, db_session, monkeypatch
):
    monkeypatch.setattr(settings, "INTEGRACAO_API_KEY", None)
    ordem_id = _ordem_aguardando_aprovacao(client, db_session)

    resposta = _notificar(unauthenticated_client, ordem_id, "aprovado")

    assert resposta.status_code == 503


def test_chave_vazia_no_ambiente_tambem_desliga_a_integracao(
    client, unauthenticated_client, db_session, monkeypatch
):
    """O compose repassa INTEGRACAO_API_KEY vazia quando a variável não foi definida."""
    monkeypatch.setattr(settings, "INTEGRACAO_API_KEY", "")
    ordem_id = _ordem_aguardando_aprovacao(client, db_session)

    resposta = _notificar(
        unauthenticated_client, ordem_id, "aprovado", headers={"X-API-Key": ""}
    )

    assert resposta.status_code == 503


def test_os_inexistente_retorna_404(unauthenticated_client, db_session):
    seed_status_ordem_servico(db_session)

    assert _notificar(unauthenticated_client, 9999, "aprovado").status_code == 404


def test_os_fora_de_aguardando_aprovacao_retorna_400(
    client, unauthenticated_client, db_session
):
    ordem_id = _ordem_aguardando_aprovacao(client, db_session)
    assert _notificar(unauthenticated_client, ordem_id, "aprovado").status_code == 200

    resposta = _notificar(unauthenticated_client, ordem_id, "recusado")

    assert resposta.status_code == 400


def test_decisao_desconhecida_retorna_422(client, unauthenticated_client, db_session):
    ordem_id = _ordem_aguardando_aprovacao(client, db_session)

    assert _notificar(unauthenticated_client, ordem_id, "talvez").status_code == 422


def _atualizar_status(cliente_http, ordem_id, acao, observacoes=None, headers=HEADERS):
    corpo = {"acao": acao}
    if observacoes is not None:
        corpo["observacoes"] = observacoes
    return cliente_http.post(
        f"/integracoes/ordens-servico/{ordem_id}/status", json=corpo, headers=headers
    )


def _ordem_recebida(client, db_session):
    seed_status_ordem_servico(db_session)
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id)
    veiculo = criar_veiculo(db_session, cliente.id, criar_marca(db_session).id)
    servico = criar_servico(db_session)
    ordem_id = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    ).json()["id"]
    return ordem_id, servico


def test_email_conduz_a_os_por_todo_o_fluxo(client, unauthenticated_client, db_session):
    ordem_id, servico = _ordem_recebida(client, db_session)

    resposta = _atualizar_status(
        unauthenticated_client, ordem_id, "iniciar_diagnostico", "Veículo na bancada"
    )
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "Em diagnóstico"

    client.post(
        f"/ordens-servico/{ordem_id}/adicionar-item",
        json={"servico_id": str(servico.id), "quantidade": 1},
    )
    assert (
        _atualizar_status(unauthenticated_client, ordem_id, "enviar_para_aprovacao")
        .json()["status"]
        == "Aguardando aprovação"
    )

    assert (
        _atualizar_status(unauthenticated_client, ordem_id, "retornar_para_diagnostico", "Pediu revisão")
        .json()["status"]
        == "Em diagnóstico"
    )
    _atualizar_status(unauthenticated_client, ordem_id, "enviar_para_aprovacao")
    assert _notificar(unauthenticated_client, ordem_id, "aprovado").status_code == 200

    assert (
        _atualizar_status(unauthenticated_client, ordem_id, "finalizar")
        .json()["status"]
        == "Finalizada"
    )
    assert (
        _atualizar_status(unauthenticated_client, ordem_id, "entregar")
        .json()["status"]
        == "Entregue"
    )


def test_atualizacao_de_status_exige_a_chave(client, unauthenticated_client, db_session):
    ordem_id, _ = _ordem_recebida(client, db_session)

    resposta = _atualizar_status(
        unauthenticated_client, ordem_id, "iniciar_diagnostico", headers={}
    )

    assert resposta.status_code == 401
    assert client.get(f"/ordens-servico/{ordem_id}").json()["status"] == "Recebida"


def test_acao_invalida_para_o_status_atual_retorna_400(
    client, unauthenticated_client, db_session
):
    ordem_id, _ = _ordem_recebida(client, db_session)

    resposta = _atualizar_status(unauthenticated_client, ordem_id, "entregar")

    assert resposta.status_code == 400


def test_acao_desconhecida_retorna_422(client, unauthenticated_client, db_session):
    ordem_id, _ = _ordem_recebida(client, db_session)

    assert _atualizar_status(unauthenticated_client, ordem_id, "explodir").status_code == 422


def test_atualizar_status_de_os_inexistente_retorna_404(unauthenticated_client, db_session):
    seed_status_ordem_servico(db_session)

    resposta = _atualizar_status(unauthenticated_client, 9999, "iniciar_diagnostico")

    assert resposta.status_code == 404
