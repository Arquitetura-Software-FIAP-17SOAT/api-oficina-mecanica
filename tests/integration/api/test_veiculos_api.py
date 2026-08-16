from tests.integration.conftest import criar_marca, criar_usuario


def _criar_cliente_via_api(client, usuario_id):
    return client.post(
        "/clientes", json={"nome": "Maria Souza", "usuario_id": usuario_id}
    ).json()


def test_fluxo_completo_de_veiculo(client, db_session):
    usuario = criar_usuario(db_session)
    marca = criar_marca(db_session)
    cliente = _criar_cliente_via_api(client, usuario.id)

    resposta_create = client.post(
        "/veiculos",
        json={
            "cliente_id": cliente["id"],
            "marca_id": marca.id,
            "placa": "ABC1D23",
            "modelo": "Gol 1.0",
        },
    )
    assert resposta_create.status_code == 201
    veiculo = resposta_create.json()
    assert veiculo["placa"] == "ABC1D23"

    veiculo_id = veiculo["id"]

    assert client.get(f"/veiculos/{veiculo_id}").status_code == 200
    assert len(client.get("/veiculos").json()) == 1
    assert (
        len(client.get(f"/veiculos?cliente_id={cliente['id']}").json()) == 1
    )

    resposta_update = client.put(
        f"/veiculos/{veiculo_id}",
        json={
            "marca_id": marca.id,
            "placa": "ABC1D23",
            "modelo": "Gol 1.6",
        },
    )
    assert resposta_update.status_code == 200
    assert resposta_update.json()["modelo"] == "Gol 1.6"

    resposta_delete = client.delete(f"/veiculos/{veiculo_id}")
    assert resposta_delete.status_code == 204

    assert client.get(f"/veiculos/{veiculo_id}").status_code == 404


def test_create_veiculo_falha_quando_cliente_nao_existe(client, db_session):
    marca = criar_marca(db_session)

    response = client.post(
        "/veiculos",
        json={
            "cliente_id": 999,
            "marca_id": marca.id,
            "placa": "ABC1D23",
            "modelo": "Gol",
        },
    )

    assert response.status_code == 400


def test_create_veiculo_falha_quando_marca_nao_existe(client, db_session):
    usuario = criar_usuario(db_session)
    cliente = _criar_cliente_via_api(client, usuario.id)

    response = client.post(
        "/veiculos",
        json={
            "cliente_id": cliente["id"],
            "marca_id": 999,
            "placa": "ABC1D23",
            "modelo": "Gol",
        },
    )

    assert response.status_code == 400


def test_operacoes_com_veiculo_inexistente_retornam_404(client):
    assert client.get("/veiculos/999").status_code == 404
    assert (
        client.put(
            "/veiculos/999",
            json={"marca_id": 1, "placa": "ABC1D23", "modelo": "Fantasma"},
        ).status_code
        == 404
    )
    assert client.delete("/veiculos/999").status_code == 404
