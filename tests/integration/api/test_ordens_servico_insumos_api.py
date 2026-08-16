"""Endpoints de peças/insumos avulsos numa ordem de serviço."""

from tests.integration.conftest import (
    criar_cliente,
    criar_insumo,
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


def _criar_ordem(client, db_session):
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)

    return client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    ).json()["id"]


def test_adicionar_insumo_com_sucesso_debita_estoque(client, db_session):
    ordem_id = _criar_ordem(client, db_session)
    insumo = criar_insumo(db_session, nome="Óleo 5W30", preco_unitario="45.90", estoque=10)

    resposta = client.post(
        f"/ordens-servico/{ordem_id}/adicionar-insumo",
        json={"insumo_id": insumo.id, "quantidade": 2},
    )

    assert resposta.status_code == 200
    assert "1" in resposta.json()["message"]

    estoque = client.get(f"/insumos/{insumo.id}").json()["estoque"]
    assert estoque == 8


def test_detalhe_da_os_mostra_insumo_utilizado(client, db_session):
    ordem_id = _criar_ordem(client, db_session)
    insumo = criar_insumo(db_session, nome="Óleo 5W30", preco_unitario="45.90", estoque=10)

    client.post(
        f"/ordens-servico/{ordem_id}/adicionar-insumo",
        json={"insumo_id": insumo.id, "quantidade": 2},
    )

    detalhe = client.get(f"/ordens-servico/{ordem_id}").json()

    assert detalhe["insumos_utilizados"] == [
        {
            "insumo_id": str(insumo.id),
            "nome": "Óleo 5W30",
            "quantidade": 2,
            "valor_unitario": 45.90,
            "valor_total": 91.80,
        }
    ]
    assert detalhe["valor_total_itens"] == 91.80


def test_adicionar_insumo_falha_com_estoque_insuficiente(client, db_session):
    ordem_id = _criar_ordem(client, db_session)
    insumo = criar_insumo(db_session, nome="Óleo 5W30", estoque=1)

    resposta = client.post(
        f"/ordens-servico/{ordem_id}/adicionar-insumo",
        json={"insumo_id": insumo.id, "quantidade": 5},
    )

    assert resposta.status_code == 400
    assert "Estoque insuficiente" in resposta.json()["detail"]

    estoque = client.get(f"/insumos/{insumo.id}").json()["estoque"]
    assert estoque == 1


def test_adicionar_insumo_falha_quando_insumo_nao_existe(client, db_session):
    ordem_id = _criar_ordem(client, db_session)

    resposta = client.post(
        f"/ordens-servico/{ordem_id}/adicionar-insumo",
        json={"insumo_id": 999, "quantidade": 1},
    )

    assert resposta.status_code == 404


def test_adicionar_insumo_falha_quando_ordem_nao_existe(client, db_session):
    insumo = criar_insumo(db_session)

    resposta = client.post(
        "/ordens-servico/999/adicionar-insumo",
        json={"insumo_id": insumo.id, "quantidade": 1},
    )

    assert resposta.status_code == 404


def test_adicionar_mesmo_insumo_duas_vezes_falha(client, db_session):
    ordem_id = _criar_ordem(client, db_session)
    insumo = criar_insumo(db_session, estoque=10)

    client.post(
        f"/ordens-servico/{ordem_id}/adicionar-insumo",
        json={"insumo_id": insumo.id, "quantidade": 1},
    )
    resposta = client.post(
        f"/ordens-servico/{ordem_id}/adicionar-insumo",
        json={"insumo_id": insumo.id, "quantidade": 1},
    )

    assert resposta.status_code == 400
    assert "já foi adicionado" in resposta.json()["detail"]


def test_remover_insumo_estorna_estoque(client, db_session):
    ordem_id = _criar_ordem(client, db_session)
    insumo = criar_insumo(db_session, estoque=10)

    client.post(
        f"/ordens-servico/{ordem_id}/adicionar-insumo",
        json={"insumo_id": insumo.id, "quantidade": 3},
    )

    resposta = client.post(
        f"/ordens-servico/{ordem_id}/remover-insumo",
        json={"insumo_id": insumo.id},
    )

    assert resposta.status_code == 200
    assert "0" in resposta.json()["message"]

    estoque = client.get(f"/insumos/{insumo.id}").json()["estoque"]
    assert estoque == 10

    detalhe = client.get(f"/ordens-servico/{ordem_id}").json()
    assert detalhe["insumos_utilizados"] == []


def test_remover_insumo_falha_quando_nao_esta_na_os(client, db_session):
    ordem_id = _criar_ordem(client, db_session)
    insumo = criar_insumo(db_session, estoque=10)

    resposta = client.post(
        f"/ordens-servico/{ordem_id}/remover-insumo",
        json={"insumo_id": insumo.id},
    )

    assert resposta.status_code == 400


def test_orcamento_automatico_considera_servicos_e_insumos(client, db_session):
    ordem_id = _criar_ordem(client, db_session)
    servico = criar_servico(db_session)  # valor 120.00
    insumo = criar_insumo(db_session, preco_unitario="30.00", estoque=10)

    client.post(f"/ordens-servico/{ordem_id}/iniciar-diagnostico", json={})
    client.post(
        f"/ordens-servico/{ordem_id}/adicionar-item",
        json={"servico_id": str(servico.id), "quantidade": 1},
    )
    client.post(
        f"/ordens-servico/{ordem_id}/adicionar-insumo",
        json={"insumo_id": insumo.id, "quantidade": 2},
    )

    resposta = client.post(f"/ordens-servico/{ordem_id}/enviar-aprovacao", json={})

    assert resposta.status_code == 200
    assert "180.00" in resposta.json()["message"]  # 120 + 2*30

    detalhe = client.get(f"/ordens-servico/{ordem_id}").json()
    assert detalhe["orcamento"] == 180.00


def _levar_ordem_a_entregue(client, ordem_id, servico_id):
    """Percorre o fluxo até 'Entregue', para testar a trava de edição de itens."""
    client.post(f"/ordens-servico/{ordem_id}/iniciar-diagnostico", json={})
    client.post(
        f"/ordens-servico/{ordem_id}/adicionar-item",
        json={"servico_id": str(servico_id), "quantidade": 1},
    )
    client.post(f"/ordens-servico/{ordem_id}/enviar-aprovacao", json={})
    client.post(f"/ordens-servico/{ordem_id}/aprovar-executar")
    client.post(f"/ordens-servico/{ordem_id}/finalizar", json={})
    client.post(f"/ordens-servico/{ordem_id}/entregar", json={})


def test_adicionar_item_falha_em_os_ja_entregue(client, db_session):
    ordem_id = _criar_ordem(client, db_session)
    servico = criar_servico(db_session)
    outro_servico = criar_servico(db_session, nome="Alinhamento")
    _levar_ordem_a_entregue(client, ordem_id, servico.id)

    resposta = client.post(
        f"/ordens-servico/{ordem_id}/adicionar-item",
        json={"servico_id": str(outro_servico.id), "quantidade": 1},
    )

    assert resposta.status_code == 400
    assert "Não é possível alterar" in resposta.json()["detail"]


def test_remover_item_falha_em_os_ja_entregue(client, db_session):
    ordem_id = _criar_ordem(client, db_session)
    servico = criar_servico(db_session)
    _levar_ordem_a_entregue(client, ordem_id, servico.id)

    resposta = client.post(
        f"/ordens-servico/{ordem_id}/remover-item",
        json={"servico_id": str(servico.id)},
    )

    assert resposta.status_code == 400
    assert "Não é possível alterar" in resposta.json()["detail"]


def test_adicionar_insumo_falha_em_os_ja_entregue(client, db_session):
    ordem_id = _criar_ordem(client, db_session)
    servico = criar_servico(db_session)
    insumo = criar_insumo(db_session, estoque=10)
    _levar_ordem_a_entregue(client, ordem_id, servico.id)

    resposta = client.post(
        f"/ordens-servico/{ordem_id}/adicionar-insumo",
        json={"insumo_id": insumo.id, "quantidade": 1},
    )

    assert resposta.status_code == 400
    assert "Não é possível alterar" in resposta.json()["detail"]

    # Não deve ter debitado o estoque: a trava barra antes de mexer no insumo
    estoque = client.get(f"/insumos/{insumo.id}").json()["estoque"]
    assert estoque == 10


def test_remover_insumo_falha_em_os_ja_entregue(client, db_session):
    ordem_id = _criar_ordem(client, db_session)
    servico = criar_servico(db_session)
    insumo = criar_insumo(db_session, estoque=10)

    client.post(f"/ordens-servico/{ordem_id}/iniciar-diagnostico", json={})
    client.post(
        f"/ordens-servico/{ordem_id}/adicionar-item",
        json={"servico_id": str(servico.id), "quantidade": 1},
    )
    client.post(
        f"/ordens-servico/{ordem_id}/adicionar-insumo",
        json={"insumo_id": insumo.id, "quantidade": 1},
    )
    client.post(f"/ordens-servico/{ordem_id}/enviar-aprovacao", json={})
    client.post(f"/ordens-servico/{ordem_id}/aprovar-executar")
    client.post(f"/ordens-servico/{ordem_id}/finalizar", json={})
    client.post(f"/ordens-servico/{ordem_id}/entregar", json={})

    resposta = client.post(
        f"/ordens-servico/{ordem_id}/remover-insumo",
        json={"insumo_id": insumo.id},
    )

    assert resposta.status_code == 400
    assert "Não é possível alterar" in resposta.json()["detail"]
