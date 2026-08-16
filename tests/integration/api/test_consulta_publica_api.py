"""Consulta de acompanhamento da OS pelo cliente, sem login administrativo.

Usa ``unauthenticated_client`` de propósito em quase todos os testes: o ponto
da funcionalidade é justamente funcionar sem token. O ``client`` autenticado
aparece só para montar o cenário pelas rotas administrativas.
"""

from tests.integration.conftest import (
    criar_cliente,
    criar_marca,
    criar_servico,
    criar_usuario,
    criar_veiculo,
    seed_status_ordem_servico,
)

CPF_CLIENTE = "52998224725"


def _cenario(db_session, client, cpf_cnpj: str | None = CPF_CLIENTE):
    """Cria cliente + veículo e abre uma OS, devolvendo o número dela."""
    seed_status_ordem_servico(db_session)
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id, cpf_cnpj=cpf_cnpj)
    marca = criar_marca(db_session)
    veiculo = criar_veiculo(db_session, cliente.id, marca.id)

    ordem_id = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    ).json()["id"]

    return ordem_id


def test_cliente_consulta_sua_os_sem_autenticacao(
    client, unauthenticated_client, db_session
):
    ordem_id = _cenario(db_session, client)

    resposta = unauthenticated_client.post(
        "/consulta/ordens-servico",
        json={"numero_os": ordem_id, "cpf_cnpj": CPF_CLIENTE},
    )

    assert resposta.status_code == 200
    body = resposta.json()
    assert body["numero_os"] == ordem_id
    assert body["status"] == "Recebida"
    assert body["status_descricao"] == "Ordem recebida, aguardando diagnóstico"
    assert body["descricao"] == "Revisão completa"
    assert body["veiculo"]["placa"] == "ABC1D23"
    assert body["aguardando_sua_aprovacao"] is False


def test_consulta_aceita_documento_com_mascara(
    client, unauthenticated_client, db_session
):
    ordem_id = _cenario(db_session, client)

    resposta = unauthenticated_client.post(
        "/consulta/ordens-servico",
        json={"numero_os": ordem_id, "cpf_cnpj": "529.982.247-25"},
    )

    assert resposta.status_code == 200


def test_consulta_nao_expoe_dados_internos(client, unauthenticated_client, db_session):
    """A resposta pública é enxuta — sem ids internos, e-mail ou observações."""
    ordem_id = _cenario(db_session, client)

    body = unauthenticated_client.post(
        "/consulta/ordens-servico",
        json={"numero_os": ordem_id, "cpf_cnpj": CPF_CLIENTE},
    ).json()

    assert "observacoes" not in body
    assert "cliente" not in body
    assert "veiculo_id" not in body
    assert set(body["veiculo"]) == {"placa", "modelo"}


def test_consulta_mostra_servicos_e_orcamento(
    client, unauthenticated_client, db_session
):
    """O cliente precisa ver o que está sendo cobrado para poder aprovar."""
    seed_status_ordem_servico(db_session)
    usuario = criar_usuario(db_session)
    cliente = criar_cliente(db_session, usuario.id, cpf_cnpj=CPF_CLIENTE)
    marca = criar_marca(db_session)
    veiculo = criar_veiculo(db_session, cliente.id, marca.id)
    servico = criar_servico(db_session)  # "Troca de óleo", valor 120.00

    ordem_id = client.post(
        "/ordens-servico",
        json={"veiculo_id": str(veiculo.id), "descricao": "Revisão completa"},
    ).json()["id"]

    client.post(f"/ordens-servico/{ordem_id}/iniciar-diagnostico", json={})
    client.post(
        f"/ordens-servico/{ordem_id}/adicionar-item",
        json={"servico_id": str(servico.id), "quantidade": 2},
    )
    client.post(f"/ordens-servico/{ordem_id}/enviar-aprovacao", json={})

    body = unauthenticated_client.post(
        "/consulta/ordens-servico",
        json={"numero_os": ordem_id, "cpf_cnpj": CPF_CLIENTE},
    ).json()

    assert body["status"] == "Aguardando aprovação"
    assert body["aguardando_sua_aprovacao"] is True
    assert body["orcamento"] == 240.00
    assert body["valor_total_servicos"] == 240.00
    assert body["servicos"] == [
        {"nome": "Troca de óleo", "quantidade": 2, "valor_total": 240.00}
    ]


def test_documento_de_outro_cliente_retorna_404(
    client, unauthenticated_client, db_session
):
    """Não basta saber o número da OS — precisa ser o dono dela."""
    ordem_id = _cenario(db_session, client)

    resposta = unauthenticated_client.post(
        "/consulta/ordens-servico",
        json={"numero_os": ordem_id, "cpf_cnpj": "111.444.777-35"},
    )

    assert resposta.status_code == 404


def test_os_inexistente_retorna_a_mesma_resposta_de_documento_errado(
    client, unauthenticated_client, db_session
):
    """404 idêntico nos dois casos: a rota não revela quais OS existem."""
    ordem_id = _cenario(db_session, client)

    documento_errado = unauthenticated_client.post(
        "/consulta/ordens-servico",
        json={"numero_os": ordem_id, "cpf_cnpj": "111.444.777-35"},
    )
    os_inexistente = unauthenticated_client.post(
        "/consulta/ordens-servico",
        json={"numero_os": 99999, "cpf_cnpj": CPF_CLIENTE},
    )

    assert documento_errado.status_code == os_inexistente.status_code == 404
    assert documento_errado.json() == os_inexistente.json()


def test_cliente_sem_documento_cadastrado_retorna_404(
    client, unauthenticated_client, db_session
):
    ordem_id = _cenario(db_session, client, cpf_cnpj=None)

    resposta = unauthenticated_client.post(
        "/consulta/ordens-servico",
        json={"numero_os": ordem_id, "cpf_cnpj": CPF_CLIENTE},
    )

    assert resposta.status_code == 404


def test_documento_vazio_retorna_404(client, unauthenticated_client, db_session):
    ordem_id = _cenario(db_session, client)

    resposta = unauthenticated_client.post(
        "/consulta/ordens-servico",
        json={"numero_os": ordem_id, "cpf_cnpj": "   "},
    )

    assert resposta.status_code == 404


def test_rota_administrativa_continua_exigindo_token(
    client, unauthenticated_client, db_session
):
    """A consulta pública não abriu a rota administrativa equivalente."""
    ordem_id = _cenario(db_session, client)

    assert unauthenticated_client.get(f"/ordens-servico/{ordem_id}").status_code == 401
