def test_fluxo_completo_de_servico(client):
    resposta_create = client.post(
        "/servicos",
        json={
            "nome": "Troca de óleo",
            "valor": "120.00",
            "descricao": "Inclui filtro",
            "tempo_estimado": "1h",
        },
    )
    assert resposta_create.status_code == 201
    servico = resposta_create.json()
    assert servico["nome"] == "Troca de óleo"

    servico_id = servico["id"]

    resposta_get = client.get(f"/servicos/{servico_id}")
    assert resposta_get.status_code == 200

    resposta_list = client.get("/servicos")
    assert resposta_list.status_code == 200
    assert len(resposta_list.json()) == 1

    resposta_update = client.put(
        f"/servicos/{servico_id}",
        json={"nome": "Troca de óleo completa", "valor": "150.00"},
    )
    assert resposta_update.status_code == 200
    assert resposta_update.json()["valor"] == "150.00" or resposta_update.json()[
        "valor"
    ] == 150.0

    resposta_delete = client.delete(f"/servicos/{servico_id}")
    assert resposta_delete.status_code == 204

    assert client.get(f"/servicos/{servico_id}").status_code == 404


def test_create_servico_falha_com_nome_duplicado(client):
    payload = {"nome": "Troca de óleo", "valor": "120.00"}

    client.post("/servicos", json=payload)
    response = client.post("/servicos", json=payload)

    assert response.status_code == 400


def test_get_servico_inexistente_retorna_404(client):
    assert client.get("/servicos/999").status_code == 404


def test_update_servico_inexistente_retorna_404(client):
    response = client.put(
        "/servicos/999", json={"nome": "Fantasma", "valor": "10.00"}
    )

    assert response.status_code == 404


def test_delete_servico_inexistente_retorna_404(client):
    assert client.delete("/servicos/999").status_code == 404
