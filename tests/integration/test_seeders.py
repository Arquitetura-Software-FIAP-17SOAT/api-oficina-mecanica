"""Seeders exercitados contra um banco SQLite de teste."""

import pytest

from adapters.database.models import (
    ClienteModel,
    MarcaModel,
    StatusOrdemServicoModel,
    UserModel,
    VeiculoModel,
)
from adapters.database.seeders.cliente_veiculo_seeder import seed_cliente_veiculo
from adapters.database.seeders.marcas_seeder import MARCAS, seed_marcas
from adapters.database.seeders.sessao import sessao_de_seed
from adapters.database.seeders.status_ordem_servico_seeder import (
    seed_status_ordem_servico,
)
from domain.value_objects.status_ordem_servico import StatusOrdemServico


def test_catalogo_de_marcas_nao_tem_repeticao():
    assert len(MARCAS) == len(set(MARCAS))


def test_seed_marcas_insere_o_catalogo_uma_unica_vez(db_session):
    seed_marcas(db_session)
    seed_marcas(db_session)

    assert db_session.query(MarcaModel).count() == len(MARCAS)


def test_seed_status_segue_a_ordem_do_enum(db_session):
    seed_status_ordem_servico(db_session)
    seed_status_ordem_servico(db_session)

    nomes = [
        s.nome
        for s in db_session.query(StatusOrdemServicoModel)
        .order_by(StatusOrdemServicoModel.id)
        .all()
    ]
    assert nomes == [status.value for status in StatusOrdemServico]


def test_seed_cliente_veiculo_e_idempotente(db_session):
    seed_cliente_veiculo(db_session)
    seed_cliente_veiculo(db_session)

    assert db_session.query(UserModel).count() == 1
    assert db_session.query(ClienteModel).count() == 1
    assert db_session.query(MarcaModel).filter_by(nome="Volkswagen").count() == 1
    veiculo = db_session.query(VeiculoModel).one()
    assert (veiculo.modelo, veiculo.ano_fabricacao) == ("Polo", 2013)


def test_seed_cliente_veiculo_reaproveita_a_marca_ja_cadastrada(db_session):
    seed_marcas(db_session)

    seed_cliente_veiculo(db_session)

    assert db_session.query(MarcaModel).filter_by(nome="Volkswagen").count() == 1


def test_sessao_recebida_nao_e_fechada_pelo_seeder(db_session):
    with sessao_de_seed(db_session) as sessao:
        assert sessao is db_session

    assert db_session.query(MarcaModel).count() == 0  # sessão continua utilizável


def test_sessao_propria_desfaz_a_transacao_em_caso_de_erro(monkeypatch):
    desfeita, fechada = [], []

    class SessaoFalsa:
        def rollback(self):
            desfeita.append(1)

        def close(self):
            fechada.append(1)

    monkeypatch.setattr("adapters.database.seeders.sessao.SessionLocal", SessaoFalsa)

    with pytest.raises(RuntimeError):
        with sessao_de_seed():
            raise RuntimeError("falha no seed")

    assert (desfeita, fechada) == ([1], [1])


def test_sessao_propria_e_fechada_ao_terminar(monkeypatch):
    desfeita, fechada = [], []

    class SessaoFalsa:
        def rollback(self):
            desfeita.append(1)

        def close(self):
            fechada.append(1)

    monkeypatch.setattr("adapters.database.seeders.sessao.SessionLocal", SessaoFalsa)

    with sessao_de_seed():
        pass

    assert (desfeita, fechada) == ([], [1])


def test_executar_seeds_cria_as_tabelas_antes_de_popular(monkeypatch):
    from adapters.database.seeders import executar

    ordem = []
    monkeypatch.setattr(executar, "create_tables", lambda: ordem.append("tabelas"))
    monkeypatch.setattr(executar, "seed_marcas", lambda: ordem.append("marcas"))
    monkeypatch.setattr(executar, "seed_status_ordem_servico", lambda: ordem.append("status"))
    monkeypatch.setattr(executar, "seed_cliente_veiculo", lambda: ordem.append("cliente"))
    monkeypatch.setenv("SEED_DADOS_EXEMPLO", "true")

    executar.executar_seeds()

    assert ordem == ["tabelas", "marcas", "status", "cliente"]


def _rodar_executar_seeds(monkeypatch, exemplo):
    from adapters.database.seeders import executar

    chamadas = []
    monkeypatch.setattr(executar, "create_tables", lambda: None)
    monkeypatch.setattr(executar, "seed_marcas", lambda: chamadas.append("marcas"))
    monkeypatch.setattr(executar, "seed_status_ordem_servico", lambda: chamadas.append("status"))
    monkeypatch.setattr(executar, "seed_cliente_veiculo", lambda: chamadas.append("cliente"))
    if exemplo is None:
        monkeypatch.delenv("SEED_DADOS_EXEMPLO", raising=False)
    else:
        monkeypatch.setenv("SEED_DADOS_EXEMPLO", exemplo)

    executar.executar_seeds()
    return chamadas


def test_dados_de_exemplo_ficam_desligados_por_padrao(monkeypatch):
    assert _rodar_executar_seeds(monkeypatch, None) == ["marcas", "status"]
    assert _rodar_executar_seeds(monkeypatch, "false") == ["marcas", "status"]


def test_dados_de_exemplo_so_com_a_variavel_ligada(monkeypatch):
    assert _rodar_executar_seeds(monkeypatch, "true") == ["marcas", "status", "cliente"]


def test_dados_de_exemplo_usam_documento_e_placa_validos(db_session):
    from domain.value_objects.cpf_cnpj import CpfCnpj
    from domain.value_objects.placa import Placa

    seed_cliente_veiculo(db_session)

    cliente = db_session.query(ClienteModel).one()
    veiculo = db_session.query(VeiculoModel).one()
    assert str(CpfCnpj(cliente.cpf_cnpj)) == cliente.cpf_cnpj
    assert str(Placa(veiculo.placa)) == veiculo.placa


def test_ids_de_status_do_repositorio_batem_com_o_que_o_seeder_grava(db_session):
    from adapters.database.repositories.ordem_servico_repository_impl import (
        OrdemServicoRepositoryImpl,
    )

    seed_status_ordem_servico(db_session)

    gravados = {s.nome: s.id for s in db_session.query(StatusOrdemServicoModel).all()}
    assert OrdemServicoRepositoryImpl.STATUS_TO_ID == gravados
    assert OrdemServicoRepositoryImpl.STATUS_TO_ID["Recebida"] == 1
    assert OrdemServicoRepositoryImpl.STATUS_TO_ID["Entregue"] == 6
