"""Fixtures compartilhadas pelos testes de integração.

Os testes de integração usam um banco SQLite em memória, criado a partir
dos mesmos models SQLAlchemy usados em produção (``infrastructure.database.models``),
para exercitar os repositórios e as rotas da API com SQL de verdade — sem
depender de um PostgreSQL disponível no ambiente de testes.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from infrastructure.database.database import Base
from infrastructure.database.models import (  # noqa: F401  (registram os models no metadata)
    ClienteModel,
    HistoricoOrdemServicoModel,
    InsumoModel,
    MarcaModel,
    OrdemServicoModel,
    OrdemServicoServicoModel,
    ServicoInsumoModel,
    ServicoModel,
    StatusOrdemServicoModel,
    UserModel,
    VeiculoModel,
)


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Sessão SQLAlchemy conectada a um SQLite em memória, com o schema criado."""

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)

    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = session_local()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def seed_status_ordem_servico(db_session: Session) -> None:
    """Popula a tabela de status na mesma ordem usada em produção."""

    nomes = [
        "Recebida",
        "Em diagnóstico",
        "Aguardando aprovação",
        "Em execução",
        "Finalizada",
        "Entregue",
    ]

    db_session.add_all([StatusOrdemServicoModel(nome=nome) for nome in nomes])
    db_session.commit()


def criar_usuario(db_session: Session, **overrides) -> UserModel:
    dados = dict(nome="João Silva", email="joao@example.com", senha_hash="hash")
    dados.update(overrides)

    model = UserModel(**dados)
    db_session.add(model)
    db_session.commit()
    db_session.refresh(model)

    return model


def criar_cliente(db_session: Session, usuario_id: int, **overrides) -> ClienteModel:
    dados = dict(usuario_id=usuario_id, nome="Maria Souza", cpf_cnpj=None, email=None)
    dados.update(overrides)

    model = ClienteModel(**dados)
    db_session.add(model)
    db_session.commit()
    db_session.refresh(model)

    return model


def criar_marca(db_session: Session, **overrides) -> MarcaModel:
    dados = dict(nome="Volkswagen")
    dados.update(overrides)

    model = MarcaModel(**dados)
    db_session.add(model)
    db_session.commit()
    db_session.refresh(model)

    return model


def criar_veiculo(
    db_session: Session, cliente_id: int, marca_id: int, **overrides
) -> VeiculoModel:
    dados = dict(
        cliente_id=cliente_id,
        marca_id=marca_id,
        placa="ABC1D23",
        modelo="Gol 1.0",
        ano_fabricacao=2020,
    )
    dados.update(overrides)

    model = VeiculoModel(**dados)
    db_session.add(model)
    db_session.commit()
    db_session.refresh(model)

    return model


def criar_servico(db_session: Session, **overrides) -> ServicoModel:
    dados = dict(nome="Troca de óleo", valor="120.00")
    dados.update(overrides)

    model = ServicoModel(**dados)
    db_session.add(model)
    db_session.commit()
    db_session.refresh(model)

    return model


def criar_insumo(db_session: Session, **overrides) -> InsumoModel:
    dados = dict(
        nome="Óleo 5W30", preco_unitario="45.90", estoque=10, quantidade_minima=3
    )
    dados.update(overrides)

    model = InsumoModel(**dados)
    db_session.add(model)
    db_session.commit()
    db_session.refresh(model)

    return model
