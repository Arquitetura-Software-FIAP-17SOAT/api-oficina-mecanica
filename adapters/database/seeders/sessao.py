from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from adapters.database.database import SessionLocal


@contextmanager
def sessao_de_seed(db: Session | None = None) -> Iterator[Session]:
    """Fornece a sessão usada por um seeder.

    Sem ``db`` abre (e sempre fecha) uma sessão própria, desfazendo a transação
    se algo falhar. Com ``db`` usa a sessão recebida e não a fecha, o que
    permite exercitar os seeders com um banco de teste.
    """
    if db is not None:
        yield db
        return

    sessao = SessionLocal()
    try:
        yield sessao
    except Exception:
        sessao.rollback()
        raise
    finally:
        sessao.close()
