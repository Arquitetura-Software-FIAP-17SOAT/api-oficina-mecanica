"""Abertura de OS com cliente, veículo, serviços e peças em uma única chamada."""

from tests.integration.conftest import (
    criar_cliente,
    criar_insumo,
    criar_marca,
    criar_servico,
    criar_usuario,
    criar_veiculo,
    seed_status_ordem_servico,
)


def _cenario(db_session):
    seed_status_ordem_servico(db_session)
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id)
    veiculo = criar_veiculo(db_session, cliente.id, criar_marca(db_session).id)
    return cliente, veiculo


def test_abre_os_com_cliente_veiculo_servicos_e_pecas(client, db_session):
    cliente, veiculo = _cenario(db_session)
    servico = criar_servico(db_session)
    insumo = criar_insumo(db_session, nome="Óleo 5W30", preco_unitario="45.90", estoque=10)

    resposta = client.post(
        "/ordens-servico",
        json={
            "cliente_id": cliente.id,
            "veiculo_id": str(veiculo.id),
            "descricao": "Revisão completa",
            "servicos": [{"servico_id": str(servico.id), "quantidade": 1}],
            "insumos": [{"insumo_id": insumo.id, "quantidade": 3}],
        },
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert isinstance(corpo["id"], int)
    assert corpo["status"] == "Recebida"
    assert corpo["quantidade_servicos"] == 1
    assert corpo["quantidade_insumos"] == 1

    detalhe = client.get(f"/ordens-servico/{corpo['id']}").json()
    assert detalhe["cliente"]["id"] == cliente.id
    assert len(detalhe["itens"]) == 1
    assert len(detalhe["insumos_utilizados"]) == 1
    assert client.get(f"/insumos/{insumo.id}").json()["estoque"] == 7


def test_abertura_sem_servicos_e_pecas_continua_valida(client, db_session):
    _, veiculo = _cenario(db_session)

    resposta = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    )

    assert resposta.status_code == 201
    assert resposta.json()["quantidade_servicos"] == 0
    assert resposta.json()["quantidade_insumos"] == 0


def test_cliente_diferente_do_dono_do_veiculo_retorna_400(client, db_session):
    cliente, veiculo = _cenario(db_session)

    resposta = client.post(
        "/ordens-servico",
        json={
            "cliente_id": cliente.id + 999,
            "veiculo_id": str(veiculo.id),
            "descricao": "Revisão completa",
        },
    )

    assert resposta.status_code == 400
    assert "não pertence ao cliente" in resposta.json()["detail"]


def test_servico_inexistente_retorna_404_e_nao_cria_os(client, db_session):
    _, veiculo = _cenario(db_session)

    resposta = client.post(
        "/ordens-servico",
        json={
            "veiculo_id": str(veiculo.id),
            "descricao": "Revisão completa",
            "servicos": [{"servico_id": "9999"}],
        },
    )

    assert resposta.status_code == 404
    assert client.get("/ordens-servico").json()["total"] == 0


def test_estoque_insuficiente_nao_cria_os_nem_baixa_estoque(client, db_session):
    _, veiculo = _cenario(db_session)
    servico = criar_servico(db_session)
    insumo = criar_insumo(db_session, nome="Filtro", preco_unitario="30.00", estoque=1)

    resposta = client.post(
        "/ordens-servico",
        json={
            "veiculo_id": str(veiculo.id),
            "descricao": "Revisão completa",
            "servicos": [{"servico_id": str(servico.id)}],
            "insumos": [{"insumo_id": insumo.id, "quantidade": 5}],
        },
    )

    assert resposta.status_code == 400
    assert client.get("/ordens-servico").json()["total"] == 0
    assert client.get(f"/insumos/{insumo.id}").json()["estoque"] == 1


def test_insumo_inexistente_retorna_404(client, db_session):
    _, veiculo = _cenario(db_session)

    resposta = client.post(
        "/ordens-servico",
        json={
            "veiculo_id": str(veiculo.id),
            "descricao": "Revisão completa",
            "insumos": [{"insumo_id": 9999}],
        },
    )

    assert resposta.status_code == 404
