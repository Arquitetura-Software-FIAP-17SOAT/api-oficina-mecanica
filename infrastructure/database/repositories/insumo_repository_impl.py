from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from domain.entities.insumo import Insumo
from domain.repositories.insumo_repository import InsumoRepository
from infrastructure.database.models import InsumoModel, ServicoInsumoModel


class InsumoRepositoryImpl(InsumoRepository):
    """Persistência de insumos."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_entity(model: InsumoModel) -> Insumo:
        return Insumo(
            id=model.id,
            nome=model.nome,
            descricao=model.descricao,
            preco_unitario=model.preco_unitario,
            estoque=model.estoque or 0,
            quantidade_minima=model.quantidade_minima or 0,
        )

    async def save(self, insumo: Insumo) -> Insumo:
        model = InsumoModel(
            nome=insumo.nome,
            descricao=insumo.descricao,
            preco_unitario=(
                insumo.preco_unitario.value if insumo.preco_unitario else None
            ),
            estoque=insumo.estoque,
            quantidade_minima=insumo.quantidade_minima,
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        insumo.id = model.id

        return insumo

    async def find_by_id(self, insumo_id: int) -> Insumo | None:
        model = self.db.get(InsumoModel, insumo_id)

        return self._to_entity(model) if model else None

    async def list(self) -> list[Insumo]:
        models = (
            self.db.query(InsumoModel)
            .order_by(InsumoModel.nome)
            .all()
        )

        return [self._to_entity(model) for model in models]

    async def list_estoque_baixo(self) -> list[Insumo]:
        models = (
            self.db.query(InsumoModel)
            .filter(
                func.coalesce(InsumoModel.estoque, 0)
                <= func.coalesce(InsumoModel.quantidade_minima, 0)
            )
            .order_by(InsumoModel.nome)
            .all()
        )

        return [self._to_entity(model) for model in models]

    async def update(self, insumo: Insumo) -> Insumo:
        model = self.db.get(InsumoModel, insumo.id)

        if model is None:
            raise ValueError("Insumo não encontrado.")

        model.nome = insumo.nome
        model.descricao = insumo.descricao
        model.preco_unitario = (
            insumo.preco_unitario.value if insumo.preco_unitario else None
        )
        model.estoque = insumo.estoque
        model.quantidade_minima = insumo.quantidade_minima

        self.db.commit()

        return insumo

    async def delete(self, insumo_id: int) -> None:
        model = self.db.get(InsumoModel, insumo_id)

        if model is None:
            return

        self.db.delete(model)
        self.db.commit()

    async def exists_by_nome(self, nome: str) -> bool:
        return (
            self.db.query(InsumoModel)
            .filter(func.lower(InsumoModel.nome) == nome.strip().lower())
            .first()
            is not None
        )

    async def has_vinculos(self, insumo_id: int) -> bool:
        return (
            self.db.query(ServicoInsumoModel)
            .filter(ServicoInsumoModel.insumo_id == insumo_id)
            .first()
            is not None
        )

    async def list_by_servico_id(self, servico_id: int) -> list[Insumo]:
        models = (
            self.db.query(InsumoModel)
            .join(
                ServicoInsumoModel,
                ServicoInsumoModel.insumo_id == InsumoModel.id,
            )
            .filter(ServicoInsumoModel.servico_id == servico_id)
            .order_by(InsumoModel.nome)
            .all()
        )

        return [self._to_entity(model) for model in models]
