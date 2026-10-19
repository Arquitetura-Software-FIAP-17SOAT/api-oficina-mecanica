"""Ordenação por prioridade de status e exclusão lógica de OS encerradas."""

from tests.integration.conftest import (
    criar_cliente,
    criar_marca,
    criar_servico,
    criar_usuario,
    criar_veiculo,
    seed_status_ordem_servico,
)


def _abrir(client, veiculo, descricao):
    return client.post(
        "/ordens-servico",
        json={
            "veiculo_id": str(veiculo.id),
            "cliente_id": veiculo.cliente_id,
            "descricao": descricao,
        },
    ).json()["id"]


def _avancar(client, ordem_id, servico_id, ate):
    """Leva a OS até o status desejado pelo fluxo normal."""
    etapas = [
        ("Em diagnóstico", "iniciar-diagnostico", {}),
        ("Aguardando aprovação", "enviar-aprovacao", {}),
        ("Em execução", "aprovar-executar", None),
        ("Finalizada", "finalizar", {}),
        ("Entregue", "entregar", {}),
    ]
    for status, acao, corpo in etapas:
        if acao == "enviar-aprovacao":
            client.post(
                f"/ordens-servico/{ordem_id}/adicionar-item",
                json={"servico_id": str(servico_id), "quantidade": 1},
            )
        resposta = client.post(f"/ordens-servico/{ordem_id}/{acao}", json=corpo)
        assert resposta.status_code == 200, resposta.text
        if status == ate:
            return


def _cenario(client, db_session):
    seed_status_ordem_servico(db_session)
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id)
    veiculo = criar_veiculo(db_session, cliente.id, criar_marca(db_session).id)
    servico = criar_servico(db_session)

    ids = {}
    for nome, destino in [
        ("recebida_1", None),
        ("recebida_2", None),
        ("diagnostico", "Em diagnóstico"),
        ("aguardando", "Aguardando aprovação"),
        ("execucao", "Em execução"),
        ("finalizada", "Finalizada"),
        ("entregue", "Entregue"),
    ]:
        ids[nome] = _abrir(client, veiculo, nome)
        if destino:
            _avancar(client, ids[nome], servico.id, destino)

    return ids


def test_listagem_ordena_por_prioridade_de_status_e_antiguidade(client, db_session):
    ids = _cenario(client, db_session)

    itens = client.get("/ordens-servico").json()["itens"]

    assert [item["id"] for item in itens] == [
        ids["execucao"],
        ids["aguardando"],
        ids["diagnostico"],
        ids["recebida_1"],  # mesma situação: a mais antiga primeiro
        ids["recebida_2"],
    ]


def test_listagem_exclui_finalizadas_e_entregues(client, db_session):
    ids = _cenario(client, db_session)

    corpo = client.get("/ordens-servico").json()

    assert corpo["total"] == 5
    listados = {item["id"] for item in corpo["itens"]}
    assert ids["finalizada"] not in listados
    assert ids["entregue"] not in listados


def test_exclusao_e_logica_a_os_encerrada_continua_consultavel(client, db_session):
    ids = _cenario(client, db_session)

    resposta = client.get(f"/ordens-servico/{ids['finalizada']}")

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "Finalizada"


def test_filtrar_por_status_encerrado_nao_lista_nada(client, db_session):
    _cenario(client, db_session)

    corpo = client.get("/ordens-servico?status=Entregue").json()

    assert corpo["total"] == 0
    assert corpo["itens"] == []


def test_paginacao_respeita_a_ordenacao(client, db_session):
    ids = _cenario(client, db_session)

    pagina_1 = client.get("/ordens-servico?page=1&page_size=2").json()
    pagina_2 = client.get("/ordens-servico?page=2&page_size=2").json()

    assert [i["id"] for i in pagina_1["itens"]] == [ids["execucao"], ids["aguardando"]]
    assert [i["id"] for i in pagina_2["itens"]] == [
        ids["diagnostico"],
        ids["recebida_1"],
    ]
    assert pagina_1["total"] == 5
