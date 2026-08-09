from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from domain.entities.servico import Servico
from domain.repositories.servico_repository import ServicoRepository
from infrastructure.database.models import (
    OrdemServicoServicoModel,
    ServicoInsumoModel,
    ServicoModel,
)


class ServicoRepositoryImpl(ServicoRepository):
    """Persistência de serviços."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_entity(model: ServicoModel) -> Servico:
        return Servico(
            id=model.id,
            nome=model.nome,
            valor=model.valor,
            descricao=model.descricao,
            tempo_estimado=model.tempo_estimado,
        )

    async def save(self, servico: Servico) -> Servico:
        model = ServicoModel(
            nome=servico.nome,
            valor=servico.valor.value,
            descricao=servico.descricao,
            tempo_estimado=servico.tempo_estimado,
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        servico.id = model.id

        return servico

    async def find_by_id(self, servico_id: int) -> Servico | None:
        model = self.db.get(ServicoModel, servico_id)

        return self._to_entity(model) if model else None

    async def list(self) -> list[Servico]:
        models = (
            self.db.query(ServicoModel)
            .order_by(ServicoModel.nome)
            .all()
        )

        return [self._to_entity(model) for model in models]

    async def update(self, servico: Servico) -> Servico:
        model = self.db.get(ServicoModel, servico.id)

        if model is None:
            raise ValueError("Serviço não encontrado.")

        model.nome = servico.nome
        model.valor = servico.valor.value
        model.descricao = servico.descricao
        model.tempo_estimado = servico.tempo_estimado

        self.db.commit()

        return servico

    async def delete(self, servico_id: int) -> None:
        model = self.db.get(ServicoModel, servico_id)

        if model is None:
            return

        self.db.delete(model)
        self.db.commit()

    async def exists_by_nome(self, nome: str) -> bool:
        return (
            self.db.query(ServicoModel)
            .filter(func.lower(ServicoModel.nome) == nome.strip().lower())
            .first()
            is not None
        )

    async def has_vinculos(self, servico_id: int) -> bool:
        tem_insumos = (
            self.db.query(ServicoInsumoModel)
            .filter(ServicoInsumoModel.servico_id == servico_id)
            .first()
            is not None
        )

        if tem_insumos:
            return True

        return (
            self.db.query(OrdemServicoServicoModel)
            .filter(OrdemServicoServicoModel.servico_id == servico_id)
            .first()
            is not None
        )
