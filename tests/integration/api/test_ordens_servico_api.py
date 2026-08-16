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


def test_fluxo_completo_da_ordem_de_servico(client, db_session):
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)
    servico = criar_servico(db_session)

    resposta_create = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    )
    assert resposta_create.status_code == 201
    ordem = resposta_create.json()
    assert ordem["status"] == "Recebida"

    ordem_id = ordem["id"]

    resposta_get = client.get(f"/ordens-servico/{ordem_id}")
    assert resposta_get.status_code == 200
    assert resposta_get.json()["quantidade_servicos"] == 0

    resposta_diagnostico = client.post(
        f"/ordens-servico/{ordem_id}/iniciar-diagnostico",
        json={"observacoes": "Verificando motor"},
    )
    assert resposta_diagnostico.status_code == 200
    assert resposta_diagnostico.json()["status"] == "Em diagnóstico"

    resposta_aprovacao = client.post(
        f"/ordens-servico/{ordem_id}/enviar-aprovacao",
        json={"orcamento": 200.0, "observacoes": "Aguardando cliente"},
    )
    assert resposta_aprovacao.status_code == 200
    assert resposta_aprovacao.json()["status"] == "Aguardando aprovação"

    resposta_item = client.post(
        f"/ordens-servico/{ordem_id}/adicionar-item",
        json={"servico_id": str(servico.id), "quantidade": 1},
    )
    assert resposta_item.status_code == 200
    assert "1" in resposta_item.json()["message"]

    resposta_remover = client.post(
        f"/ordens-servico/{ordem_id}/remover-item",
        json={"servico_id": str(servico.id)},
    )
    assert resposta_remover.status_code == 200

    client.post(
        f"/ordens-servico/{ordem_id}/adicionar-item",
        json={"servico_id": str(servico.id), "quantidade": 1},
    )

    resposta_aprovar = client.post(f"/ordens-servico/{ordem_id}/aprovar-executar")
    assert resposta_aprovar.status_code == 200
    assert resposta_aprovar.json()["status"] == "Em execução"

    resposta_finalizar = client.post(
        f"/ordens-servico/{ordem_id}/finalizar", json={"observacoes": "Pronto"}
    )
    assert resposta_finalizar.status_code == 200
    assert resposta_finalizar.json()["status"] == "Finalizada"

    resposta_entregar = client.post(
        f"/ordens-servico/{ordem_id}/entregar", json={"observacoes": "Entregue"}
    )
    assert resposta_entregar.status_code == 200
    assert resposta_entregar.json()["status"] == "Entregue"


def test_retornar_para_diagnostico(client, db_session):
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)

    ordem_id = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    ).json()["id"]

    client.post(f"/ordens-servico/{ordem_id}/iniciar-diagnostico", json={})
    client.post(
        f"/ordens-servico/{ordem_id}/enviar-aprovacao", json={"orcamento": 100.0}
    )

    response = client.post(
        f"/ordens-servico/{ordem_id}/retornar-diagnostico",
        json={"motivo": "Cliente pediu revisão"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Em diagnóstico"


def test_criar_ordem_falha_quando_veiculo_nao_existe(client, db_session):
    seed_status_ordem_servico(db_session)

    response = client.post(
        "/ordens-servico",
        json={"veiculo_id": "999", "descricao": "Revisão completa"},
    )

    assert response.status_code == 404


def test_obter_ordem_inexistente_retorna_404(client, db_session):
    seed_status_ordem_servico(db_session)

    response = client.get("/ordens-servico/999")

    assert response.status_code == 404


def test_transicao_invalida_retorna_400(client, db_session):
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)

    ordem_id = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    ).json()["id"]

    # Não é possível aprovar direto sem passar por diagnóstico/aprovação
    response = client.post(f"/ordens-servico/{ordem_id}/aprovar-executar")

    assert response.status_code == 400


def test_adicionar_item_falha_quando_servico_nao_existe(client, db_session):
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)

    ordem_id = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    ).json()["id"]

    response = client.post(
        f"/ordens-servico/{ordem_id}/adicionar-item",
        json={"servico_id": "999", "quantidade": 1},
    )

    assert response.status_code == 404


def test_operacoes_com_ordem_inexistente_retornam_404(client, db_session):
    seed_status_ordem_servico(db_session)

    assert (
        client.post(
            "/ordens-servico/999/iniciar-diagnostico", json={}
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/ordens-servico/999/enviar-aprovacao", json={"orcamento": 10.0}
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/ordens-servico/999/adicionar-item",
            json={"servico_id": "1", "quantidade": 1},
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/ordens-servico/999/remover-item", json={"servico_id": "1"}
        ).status_code
        == 404
    )
    assert client.post("/ordens-servico/999/aprovar-executar").status_code == 404
    assert (
        client.post("/ordens-servico/999/finalizar", json={}).status_code == 404
    )
    assert (
        client.post("/ordens-servico/999/entregar", json={}).status_code == 404
    )
    assert (
        client.post(
            "/ordens-servico/999/retornar-diagnostico", json={}
        ).status_code
        == 404
    )
