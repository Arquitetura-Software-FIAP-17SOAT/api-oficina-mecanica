def test_register_user_com_sucesso(client):
    response = client.post(
        "/users/register",
        json={
            "name": "João Silva",
            "email": "joao@example.com",
            "password": "senha123",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] is not None
    assert "sucesso" in body["message"]


def test_register_user_falha_com_email_duplicado(client):
    payload = {
        "name": "João Silva",
        "email": "joao@example.com",
        "password": "senha123",
    }

    client.post("/users/register", json=payload)
    response = client.post("/users/register", json=payload)

    assert response.status_code == 400
    assert "já cadastrado" in response.json()["detail"].lower()


def test_login_com_sucesso(client):
    client.post(
        "/users/register",
        json={
            "name": "João Silva",
            "email": "joao@example.com",
            "password": "senha123",
        },
    )

    response = client.post(
        "/users/login",
        json={"email": "joao@example.com", "password": "senha123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_falha_com_credenciais_invalidas(client):
    response = client.post(
        "/users/login",
        json={"email": "nao-existe@example.com", "password": "senha123"},
    )

    assert response.status_code == 401
