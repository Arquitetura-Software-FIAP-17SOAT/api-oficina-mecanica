import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


def ler_booleano(nome: str, padrao: bool = False) -> bool:
    """Lê uma variável de ambiente booleana (true/1/yes/on, sem diferenciar caixa)."""
    valor = os.getenv(nome)
    if valor is None:
        return padrao
    return valor.strip().lower() in {"1", "true", "yes", "on"}


engine = create_engine(
    DATABASE_URL,
    # Imprime todo o SQL executado; ligue com SQL_ECHO=true só para depurar.
    echo=ler_booleano("SQL_ECHO"),
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
    from adapters.database.models import ( 
        UserModel,
        ClienteModel,
        MarcaModel,
        VeiculoModel,
        ServicoModel,
        InsumoModel,
        ServicoInsumoModel,
        OrdemServicoModel,
        OrdemServicoServicoModel,
        OrdemServicoInsumoModel,
        StatusOrdemServicoModel,
        HistoricoOrdemServicoModel,
    )

    Base.metadata.create_all(bind=engine)