def test_fluxo_completo_de_insumo(client):
    resposta_create = client.post(
        "/insumos",
        json={
            "nome": "Óleo 5W30",
            "preco_unitario": "45.90",
            "estoque": 10,
            "quantidade_minima": 3,
        },
    )
    assert resposta_create.status_code == 201
    insumo = resposta_create.json()
    assert insumo["estoque"] == 10
    assert insumo["estoque_baixo"] is False

    insumo_id = insumo["id"]

    resposta_get = client.get(f"/insumos/{insumo_id}")
    assert resposta_get.status_code == 200

    resposta_list = client.get("/insumos")
    assert resposta_list.status_code == 200
    assert len(resposta_list.json()) == 1

    resposta_update = client.put(
        f"/insumos/{insumo_id}",
        json={"nome": "Óleo 5W30 sintético", "quantidade_minima": 5},
    )
    assert resposta_update.status_code == 200
    assert resposta_update.json()["nome"] == "Óleo 5W30 sintético"

    resposta_entrada = client.post(
        f"/insumos/{insumo_id}/estoque/entrada", json={"quantidade": 5}
    )
    assert resposta_entrada.status_code == 200
    assert resposta_entrada.json()["estoque"] == 15

    resposta_saida = client.post(
        f"/insumos/{insumo_id}/estoque/saida", json={"quantidade": 3}
    )
    assert resposta_saida.status_code == 200
    assert resposta_saida.json()["estoque"] == 12

    resposta_ajuste = client.post(
        f"/insumos/{insumo_id}/estoque/ajuste", json={"quantidade": 1}
    )
    assert resposta_ajuste.status_code == 200
    assert resposta_ajuste.json()["estoque"] == 1
    assert resposta_ajuste.json()["estoque_baixo"] is True

    resposta_baixo = client.get("/insumos/estoque-baixo")
    assert resposta_baixo.status_code == 200
    assert len(resposta_baixo.json()) == 1

    resposta_delete = client.delete(f"/insumos/{insumo_id}")
    assert resposta_delete.status_code == 204

    assert client.get(f"/insumos/{insumo_id}").status_code == 404


def test_create_insumo_falha_com_nome_duplicado(client):
    payload = {"nome": "Filtro de combustivel"}

    client.post("/insumos", json=payload)
    response = client.post("/insumos", json=payload)

    assert response.status_code == 400


def test_estoque_saida_falha_quando_insuficiente(client):
    insumo = client.post("/insumos", json={"nome": "Óleo", "estoque": 1}).json()

    response = client.post(
        f"/insumos/{insumo['id']}/estoque/saida", json={"quantidade": 5}
    )

    assert response.status_code == 400


def test_operacoes_com_insumo_inexistente_retornam_404(client):
    assert client.get("/insumos/999").status_code == 404
    assert (
        client.put("/insumos/999", json={"nome": "Fantasma"}).status_code == 404
    )
    assert client.delete("/insumos/999").status_code == 404
    assert (
        client.post(
            "/insumos/999/estoque/entrada", json={"quantidade": 1}
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/insumos/999/estoque/saida", json={"quantidade": 1}
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/insumos/999/estoque/ajuste", json={"quantidade": 1}
        ).status_code
        == 404
    )


def test_operacoes_sem_autenticacao_retornam_401(unauthenticated_client):
    assert (
        unauthenticated_client.post("/insumos", json={"nome": "Óleo"}).status_code
        == 401
    )
    assert unauthenticated_client.get("/insumos").status_code == 401
    assert (
        unauthenticated_client.post(
            "/insumos/1/estoque/entrada", json={"quantidade": 1}
        ).status_code
        == 401
    )
