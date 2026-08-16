from tests.integration.conftest import criar_marca, criar_usuario, criar_veiculo


def test_fluxo_completo_de_cliente(client, db_session):
    usuario = criar_usuario(db_session)

    resposta_create = client.post(
        "/clientes",
        json={
            "nome": "Maria Souza",
            "usuario_id": usuario.id,
            "cpf_cnpj": "529.982.247-25",
            "email": "maria@example.com",
        },
    )
    assert resposta_create.status_code == 201
    cliente = resposta_create.json()
    assert cliente["nome"] == "Maria Souza"
    assert cliente["cpf_cnpj"] == "52998224725"

    cliente_id = cliente["id"]

    resposta_get = client.get(f"/clientes/{cliente_id}")
    assert resposta_get.status_code == 200

    resposta_list = client.get("/clientes")
    assert resposta_list.status_code == 200
    assert len(resposta_list.json()) == 1

    resposta_update = client.put(
        f"/clientes/{cliente_id}",
        json={"nome": "Maria Souza Lima", "email": "maria.lima@example.com"},
    )
    assert resposta_update.status_code == 200
    assert resposta_update.json()["nome"] == "Maria Souza Lima"

    resposta_delete = client.delete(f"/clientes/{cliente_id}")
    assert resposta_delete.status_code == 204

    assert client.get(f"/clientes/{cliente_id}").status_code == 404


def test_create_cliente_falha_quando_usuario_nao_existe(client):
    response = client.post(
        "/clientes", json={"nome": "Maria Souza", "usuario_id": 999}
    )

    assert response.status_code == 400


def test_get_cliente_inexistente_retorna_404(client):
    response = client.get("/clientes/999")

    assert response.status_code == 404


def test_update_cliente_inexistente_retorna_404(client):
    response = client.put("/clientes/999", json={"nome": "Fantasma"})

    assert response.status_code == 404


def test_delete_cliente_com_veiculo_retorna_400(client, db_session):
    usuario = criar_usuario(db_session)
    marca = criar_marca(db_session)

    resposta_create = client.post(
        "/clientes", json={"nome": "Maria Souza", "usuario_id": usuario.id}
    )
    cliente_id = resposta_create.json()["id"]

    criar_veiculo(db_session, cliente_id, marca.id)

    response = client.delete(f"/clientes/{cliente_id}")

    assert response.status_code == 400


def test_delete_cliente_inexistente_retorna_404(client):
    response = client.delete("/clientes/999")

    assert response.status_code == 404
