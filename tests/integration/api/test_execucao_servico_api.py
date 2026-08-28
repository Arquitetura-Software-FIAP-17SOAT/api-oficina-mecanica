from datetime import datetime, timedelta

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


def _criar_ordem_em_execucao(client, db_session, servico_id):
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)

    ordem_id = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    ).json()["id"]
    client.post(f"/ordens-servico/{ordem_id}/iniciar-diagnostico", json={})
    client.post(
        f"/ordens-servico/{ordem_id}/enviar-aprovacao",
        json={"orcamento": 200.0},
    )
    client.post(
        f"/ordens-servico/{ordem_id}/adicionar-item",
        json={"servico_id": str(servico_id), "quantidade": 1},
    )
    client.post(f"/ordens-servico/{ordem_id}/aprovar-executar")

    return ordem_id


def test_iniciar_execucao_com_sucesso(client, db_session):
    servico = criar_servico(db_session)
    ordem_id = _criar_ordem_em_execucao(client, db_session, servico.id)

    response = client.post(
        f"/ordens-servico/{ordem_id}/servicos/{servico.id}/iniciar",
        json={"data_inicio": "2025-01-15T10:00:00"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ordem_servico_id"] == ordem_id
    assert body["servico_id"] == servico.id
    assert body["data_inicio"].startswith("2025-01-15T10:00:00")
    assert body["data_fim"] is None


def test_impede_iniciar_execucao_duas_vezes(client, db_session):
    servico = criar_servico(db_session)
    ordem_id = _criar_ordem_em_execucao(client, db_session, servico.id)
    path = f"/ordens-servico/{ordem_id}/servicos/{servico.id}/iniciar"

    assert client.post(path, json={"data_inicio": "2025-01-15T10:00:00"}).status_code == 200
    response = client.post(path, json={"data_inicio": "2025-01-15T11:00:00"})

    assert response.status_code == 400
    assert "já foi iniciado" in response.json()["detail"]


def test_finalizar_execucao_com_sucesso_e_calcula_tempo(client, db_session):
    servico = criar_servico(db_session)
    ordem_id = _criar_ordem_em_execucao(client, db_session, servico.id)
    base = datetime(2025, 1, 15, 10, 0, 0)

    client.post(
        f"/ordens-servico/{ordem_id}/servicos/{servico.id}/iniciar",
        json={"data_inicio": base.isoformat()},
    )
    response = client.post(
        f"/ordens-servico/{ordem_id}/servicos/{servico.id}/finalizar",
        json={"data_fim": (base + timedelta(hours=2, minutes=30)).isoformat()},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data_fim"].startswith("2025-01-15T12:30:00")
    assert body["tempo_execucao_horas"] == 2.5


def test_impede_finalizar_execucao_sem_iniciar(client, db_session):
    servico = criar_servico(db_session)
    ordem_id = _criar_ordem_em_execucao(client, db_session, servico.id)

    response = client.post(
        f"/ordens-servico/{ordem_id}/servicos/{servico.id}/finalizar",
        json={"data_fim": "2025-01-15T12:00:00"},
    )

    assert response.status_code == 400
    assert "não foi iniciado" in response.json()["detail"]


def test_impede_finalizar_execucao_duas_vezes(client, db_session):
    servico = criar_servico(db_session)
    ordem_id = _criar_ordem_em_execucao(client, db_session, servico.id)
    path = f"/ordens-servico/{ordem_id}/servicos/{servico.id}"

    client.post(f"{path}/iniciar", json={"data_inicio": "2025-01-15T10:00:00"})
    assert client.post(f"{path}/finalizar", json={"data_fim": "2025-01-15T11:00:00"}).status_code == 200
    response = client.post(f"{path}/finalizar", json={"data_fim": "2025-01-15T12:00:00"})

    assert response.status_code == 400
    assert "já foi finalizado" in response.json()["detail"]


def test_retorna_404_para_ordem_inexistente(client, db_session):
    servico = criar_servico(db_session)
    seed_status_ordem_servico(db_session)

    iniciar = client.post(
        f"/ordens-servico/999/servicos/{servico.id}/iniciar",
        json={},
    )
    finalizar = client.post(
        f"/ordens-servico/999/servicos/{servico.id}/finalizar",
        json={},
    )

    assert iniciar.status_code == 404
    assert "não encontrada" in iniciar.json()["detail"]
    assert finalizar.status_code == 404
    assert "não encontrada" in finalizar.json()["detail"]


def test_iniciar_e_finalizar_sem_data_usam_a_hora_atual(client, db_session):
    """O caminho default (sem data no corpo) deve funcionar em qualquer fuso.

    Regressão: a data era normalizada para UTC naive mas comparada com a hora
    local naive, então em servidores a oeste de UTC o default sempre caía em
    "data no futuro".
    """
    servico = criar_servico(db_session)
    ordem_id = _criar_ordem_em_execucao(client, db_session, servico.id)

    inicio = client.post(
        f"/ordens-servico/{ordem_id}/servicos/{servico.id}/iniciar",
        json={},
    )
    fim = client.post(
        f"/ordens-servico/{ordem_id}/servicos/{servico.id}/finalizar",
        json={},
    )

    assert inicio.status_code == 200
    assert inicio.json()["data_inicio"] is not None
    assert fim.status_code == 200
    assert fim.json()["data_fim"] is not None


def test_retorna_erro_para_servico_nao_associado_a_os(client, db_session):
    servico = criar_servico(db_session)
    outro_servico = criar_servico(db_session, nome="Alinhamento")
    ordem_id = _criar_ordem_em_execucao(client, db_session, servico.id)

    response = client.post(
        f"/ordens-servico/{ordem_id}/servicos/{outro_servico.id}/iniciar",
        json={},
    )

    assert response.status_code == 400
    assert "não encontrado na ordem" in response.json()["detail"]


def test_impede_datas_de_inicio_e_fim_no_futuro(client, db_session):
    servico = criar_servico(db_session)
    ordem_id = _criar_ordem_em_execucao(client, db_session, servico.id)
    futuro = (datetime.now() + timedelta(days=1)).replace(microsecond=0).isoformat()

    inicio = client.post(
        f"/ordens-servico/{ordem_id}/servicos/{servico.id}/iniciar",
        json={"data_inicio": futuro},
    )

    assert inicio.status_code == 400
    assert "não pode ser no futuro" in inicio.json()["detail"]

    client.post(
        f"/ordens-servico/{ordem_id}/servicos/{servico.id}/iniciar",
        json={"data_inicio": "2025-01-15T10:00:00"},
    )
    fim = client.post(
        f"/ordens-servico/{ordem_id}/servicos/{servico.id}/finalizar",
        json={"data_fim": futuro},
    )

    assert fim.status_code == 400
    assert "não pode ser no futuro" in fim.json()["detail"]


def test_impede_data_final_anterior_a_data_inicial(client, db_session):
    servico = criar_servico(db_session)
    ordem_id = _criar_ordem_em_execucao(client, db_session, servico.id)

    client.post(
        f"/ordens-servico/{ordem_id}/servicos/{servico.id}/iniciar",
        json={"data_inicio": "2025-01-15T12:00:00"},
    )
    response = client.post(
        f"/ordens-servico/{ordem_id}/servicos/{servico.id}/finalizar",
        json={"data_fim": "2025-01-15T11:00:00"},
    )

    assert response.status_code == 400
    assert "anterior à data de início" in response.json()["detail"]


def test_endpoints_de_execucao_nao_aceitam_patch(client, db_session):
    servico = criar_servico(db_session)
    ordem_id = _criar_ordem_em_execucao(client, db_session, servico.id)

    response = client.patch(
        f"/ordens-servico/{ordem_id}/servicos/{servico.id}/iniciar",
        json={},
    )

    assert response.status_code == 405


def test_metricas_tempo_medio_execucao_vazia_sem_execucoes(client, db_session):
    response = client.get("/ordens-servico/metricas/tempo-medio-execucao")

    assert response.status_code == 200
    assert response.json() == []


def test_metricas_tempo_medio_execucao_exige_autenticacao(
    client, unauthenticated_client, db_session
):
    response = unauthenticated_client.get(
        "/ordens-servico/metricas/tempo-medio-execucao"
    )

    assert response.status_code == 401


def test_metrica_sobrevive_as_transicoes_seguintes_da_os(client, db_session):
    """Fluxo normal completo: executa serviço → finaliza OS → entrega.

    Regressão: o ``save`` da OS apagava e regravava os itens sem as colunas
    ``data_inicio``/``data_fim``, então finalizar a OS destruía a métrica de
    tempo médio recém-capturada.
    """
    servico = criar_servico(db_session)
    ordem_id = _criar_ordem_em_execucao(client, db_session, servico.id)
    base = datetime(2025, 1, 15, 10, 0, 0)

    client.post(
        f"/ordens-servico/{ordem_id}/servicos/{servico.id}/iniciar",
        json={"data_inicio": base.isoformat()},
    )
    client.post(
        f"/ordens-servico/{ordem_id}/servicos/{servico.id}/finalizar",
        json={"data_fim": (base + timedelta(hours=2, minutes=30)).isoformat()},
    )

    assert (
        client.post(f"/ordens-servico/{ordem_id}/finalizar", json={}).status_code
        == 200
    )
    assert (
        client.post(f"/ordens-servico/{ordem_id}/entregar", json={}).status_code
        == 200
    )

    response = client.get("/ordens-servico/metricas/tempo-medio-execucao")

    assert response.status_code == 200
    assert response.json() == [
        {
            "servico_id": servico.id,
            "nome_servico": "Troca de óleo",
            "tempo_medio_horas": 2.5,
            "quantidade_execucoes": 1,
        }
    ]


def test_impede_iniciar_execucao_fora_do_status_em_execucao(client, db_session):
    seed_status_ordem_servico(db_session)
    veiculo = _criar_veiculo(db_session)
    servico = criar_servico(db_session)
    ordem_id = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    ).json()["id"]

    response = client.post(
        f"/ordens-servico/{ordem_id}/servicos/{servico.id}/iniciar",
        json={},
    )

    assert response.status_code == 400
    assert "precisa estar em execução" in response.json()["detail"]