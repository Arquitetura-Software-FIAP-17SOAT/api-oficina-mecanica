from sqlalchemy.orm import Session

from application.ports.unit_of_work import UnitOfWork

_TRANSACAO_ATIVA = "transacao_ativa"


def persistir(db: Session) -> None:
    """Confirma a escrita de um repositório.

    Fora de uma unidade de trabalho cada escrita é confirmada na hora (comportamento
    de sempre). Dentro de uma, só envia ao banco (``flush``) e deixa a confirmação
    para o fim do bloco, para que várias escritas valham como uma só.
    """
    if db.info.get(_TRANSACAO_ATIVA):
        db.flush()
    else:
        db.commit()


class SqlAlchemyUnitOfWork(UnitOfWork):
    """Unidade de trabalho sobre a sessão SQLAlchemy da requisição."""

    def __init__(self, db: Session):
        self.db = db

    def iniciar(self) -> None:
        self.db.info[_TRANSACAO_ATIVA] = True

    def confirmar(self) -> None:
        self.db.info.pop(_TRANSACAO_ATIVA, None)
        self.db.commit()

    def desfazer(self) -> None:
        self.db.info.pop(_TRANSACAO_ATIVA, None)
        self.db.rollback()
