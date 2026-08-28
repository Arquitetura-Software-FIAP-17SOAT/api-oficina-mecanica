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


def test_fluxo_completo_da_ordem_de_servico(client, db_session, auth_headers):
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

    resposta_get = client.get(
        f"/ordens-servico/{ordem_id}", headers=auth_headers
    )
    assert resposta_get.status_code == 200
    detalhe = resposta_get.json()
    assert detalhe["itens"] == []
    assert detalhe["cliente"]["nome"] == "Maria Souza"
    assert detalhe["veiculo"]["placa"] == "ABC1D23"

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
        json={"servico_id": str(servico.id), "quantidade": 2},
    )

    resposta_detalhe = client.get(
        f"/ordens-servico/{ordem_id}", headers=auth_headers
    )
    item = resposta_detalhe.json()["itens"][0]
    assert item["servico_id"] == str(servico.id)
    assert item["nome"] == "Troca de óleo"
    assert item["quantidade"] == 2
    assert item["valor_total"] == item["valor_unitario"] * 2

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


def test_rejeitar_orcamento_finaliza_ordem(client, db_session, auth_headers):
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

    response = client.post(f"/ordens-servico/{ordem_id}/rejeitar-orcamento")

    assert response.status_code == 200
    assert response.json()["status"] == "Finalizada"
    detalhe = client.get(f"/ordens-servico/{ordem_id}", headers=auth_headers).json()
    assert detalhe["status_orcamento"] == "Rejeitado"
    assert detalhe["status"] == "Finalizada"


def test_criar_ordem_falha_quando_veiculo_nao_existe(client, db_session):
    seed_status_ordem_servico(db_session)

    response = client.post(
        "/ordens-servico",
        json={"veiculo_id": "999", "descricao": "Revisão completa"},
    )

    assert response.status_code == 404


def test_obter_ordem_inexistente_retorna_404(client, db_session, auth_headers):
    seed_status_ordem_servico(db_session)

    response = client.get("/ordens-servico/999", headers=auth_headers)

    assert response.status_code == 404


def test_obter_ordem_sem_autenticacao_retorna_401(
    client, unauthenticated_client, db_session
):
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)

    ordem_id = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    ).json()["id"]

    response = unauthenticated_client.get(f"/ordens-servico/{ordem_id}")

    assert response.status_code == 401


def test_listar_ordens_sem_autenticacao_retorna_401(unauthenticated_client, db_session):
    seed_status_ordem_servico(db_session)

    response = unauthenticated_client.get("/ordens-servico")

    assert response.status_code == 401


def test_criar_ordem_sem_autenticacao_retorna_401(unauthenticated_client, db_session):
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)

    response = unauthenticated_client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    )

    assert response.status_code == 401


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


def test_listar_ordens_de_servico_com_paginacao(client, db_session, auth_headers):
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)

    for _ in range(3):
        client.post(
            "/ordens-servico",
            json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
        )

    resposta = client.get(
        "/ordens-servico?page=1&page_size=2", headers=auth_headers
    )

    assert resposta.status_code == 200
    body = resposta.json()
    assert body["total"] == 3
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert body["total_paginas"] == 2
    assert len(body["itens"]) == 2

    resposta_pagina_2 = client.get(
        "/ordens-servico?page=2&page_size=2", headers=auth_headers
    )
    assert len(resposta_pagina_2.json()["itens"]) == 1


def test_listar_ordens_de_servico_filtrando_por_status(
    client, db_session, auth_headers
):
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)

    ordem_id = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    ).json()["id"]
    client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Troca de pneus"},
    )

    client.post(f"/ordens-servico/{ordem_id}/iniciar-diagnostico", json={})

    resposta = client.get(
        "/ordens-servico?status=Em diagnóstico", headers=auth_headers
    )

    assert resposta.status_code == 200
    body = resposta.json()
    assert body["total"] == 1
    assert body["itens"][0]["id"] == ordem_id


def test_listar_ordens_de_servico_filtrando_por_placa_e_cpf_cnpj(
    client, db_session, auth_headers
):
    seed_status_ordem_servico(db_session)
    usuario = criar_usuario(db_session, email="ana@example.com")
    cliente = criar_cliente(
        db_session, usuario.id, nome="Ana", cpf_cnpj="52998224725"
    )
    marca = criar_marca(db_session)
    veiculo_alvo = criar_veiculo(
        db_session, cliente.id, marca.id, placa="XYZ9A87"
    )
    outro_veiculo = _criar_veiculo(db_session)

    ordem_alvo = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo_alvo.id), "descricao": "Revisão completa"},
    ).json()["id"]
    client.post(
        "/ordens-servico",
        json={"veiculo_id": str(outro_veiculo.id), "descricao": "Troca de pneus"},
    )

    resposta_placa = client.get(
        "/ordens-servico?placa=xyz-9a87", headers=auth_headers
    )
    assert resposta_placa.json()["total"] == 1
    assert resposta_placa.json()["itens"][0]["id"] == ordem_alvo

    resposta_cpf = client.get(
        "/ordens-servico?cpf_cnpj=529.982.247-25", headers=auth_headers
    )
    assert resposta_cpf.json()["total"] == 1
    assert resposta_cpf.json()["itens"][0]["id"] == ordem_alvo


def test_listar_ordens_de_servico_com_status_invalido_retorna_400(
    client, db_session, auth_headers
):
    seed_status_ordem_servico(db_session)

    resposta = client.get(
        "/ordens-servico?status=Inexistente", headers=auth_headers
    )

    assert resposta.status_code == 400


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


def test_enviar_aprovacao_gera_orcamento_automaticamente(
    client, db_session, auth_headers
):
    """Sem 'orcamento' no corpo, a API deve orçar a partir dos serviços da OS."""
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)
    servico = criar_servico(db_session)  # valor 120.00

    ordem_id = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    ).json()["id"]

    client.post(f"/ordens-servico/{ordem_id}/iniciar-diagnostico", json={})
    client.post(
        f"/ordens-servico/{ordem_id}/adicionar-item",
        json={"servico_id": str(servico.id), "quantidade": 2},
    )

    resposta = client.post(f"/ordens-servico/{ordem_id}/enviar-aprovacao", json={})

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "Aguardando aprovação"
    assert "240.00" in resposta.json()["message"]

    detalhe = client.get(f"/ordens-servico/{ordem_id}", headers=auth_headers).json()
    assert detalhe["orcamento"] == 240.00
    assert detalhe["valor_total_itens"] == 240.00


def test_enviar_aprovacao_com_orcamento_manual_prevalece(client, db_session):
    """Valor informado no corpo sobrepõe o total calculado (desconto)."""
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)
    servico = criar_servico(db_session)  # valor 120.00

    ordem_id = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    ).json()["id"]

    client.post(f"/ordens-servico/{ordem_id}/iniciar-diagnostico", json={})
    client.post(
        f"/ordens-servico/{ordem_id}/adicionar-item",
        json={"servico_id": str(servico.id), "quantidade": 2},
    )

    resposta = client.post(
        f"/ordens-servico/{ordem_id}/enviar-aprovacao", json={"orcamento": 200.00}
    )

    assert resposta.status_code == 200
    assert "200.00" in resposta.json()["message"]


def test_enviar_aprovacao_sem_itens_retorna_400(client, db_session):
    """Sem serviços adicionados não há o que orçar automaticamente."""
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)

    ordem_id = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    ).json()["id"]

    client.post(f"/ordens-servico/{ordem_id}/iniciar-diagnostico", json={})

    resposta = client.post(f"/ordens-servico/{ordem_id}/enviar-aprovacao", json={})

    assert resposta.status_code == 400
    assert "não possui serviços adicionados" in resposta.json()["detail"]
