import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/oficina"

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Fornece uma sessão do banco de dados por requisição."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """
    Cria todas as tabelas mapeadas pelo SQLAlchemy.
    Deve ser chamado na inicialização da aplicação.
    """
    # Importa todos os models para registrá-los no metadata
    from infrastructure.database.models import (
        UserModel,
        ClienteModel,
        MarcaModel,
        VeiculoModel,
        ServicoModel,
        InsumoModel,
        ServicoInsumoModel,
        OrdemServicoModel,
        OrdemServicoServicoModel,
        StatusOrdemServicoModel,
        HistoricoOrdemServicoModel,
    )

    Base.metadata.create_all(bind=engine)