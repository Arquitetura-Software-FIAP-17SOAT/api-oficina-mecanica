from __future__ import annotations

from sqlalchemy.orm import Session

from domain.entities.veiculo import Veiculo
from domain.repositories.veiculo_repository import VeiculoRepository
from domain.value_objects.data_hora import DataHora
from infrastructure.database.models import (
    MarcaModel,
    OrdemServicoModel,
    VeiculoModel,
)


class VeiculoRepositoryImpl(VeiculoRepository):
    """Persistência de veículos."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_entity(model: VeiculoModel) -> Veiculo:
        return Veiculo(
            id=model.id,
            cliente_id=model.cliente_id,
            marca_id=model.marca_id,
            placa=model.placa,
            modelo=model.modelo,
            chassi=model.chassi,
            ano_fabricacao=model.ano_fabricacao,
            criado_em=model.criado_em,
        )

    async def save(self, veiculo: Veiculo) -> Veiculo:
        model = VeiculoModel(
            cliente_id=veiculo.cliente_id,
            marca_id=veiculo.marca_id,
            placa=str(veiculo.placa),
            modelo=veiculo.modelo,
            chassi=str(veiculo.chassi) if veiculo.chassi else None,
            ano_fabricacao=veiculo.ano_fabricacao,
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        veiculo.id = model.id
        veiculo.criado_em = (
            DataHora(model.criado_em) if model.criado_em is not None else None
        )

        return veiculo

    async def find_by_id(self, veiculo_id: int) -> Veiculo | None:
        model = self.db.get(VeiculoModel, veiculo_id)

        return self._to_entity(model) if model else None

    async def list(self, cliente_id: int | None = None) -> list[Veiculo]:
        query = self.db.query(VeiculoModel)

        if cliente_id is not None:
            query = query.filter(VeiculoModel.cliente_id == cliente_id)

        models = query.order_by(VeiculoModel.placa).all()

        return [self._to_entity(model) for model in models]

    async def update(self, veiculo: Veiculo) -> Veiculo:
        model = self.db.get(VeiculoModel, veiculo.id)

        if model is None:
            raise ValueError("Veículo não encontrado.")

        model.marca_id = veiculo.marca_id
        model.placa = str(veiculo.placa)
        model.modelo = veiculo.modelo
        model.chassi = str(veiculo.chassi) if veiculo.chassi else None
        model.ano_fabricacao = veiculo.ano_fabricacao

        self.db.commit()

        return veiculo

    async def delete(self, veiculo_id: int) -> None:
        model = self.db.get(VeiculoModel, veiculo_id)

        if model is None:
            return

        self.db.delete(model)
        self.db.commit()

    async def exists_by_placa(self, placa: str) -> bool:
        return (
            self.db.query(VeiculoModel)
            .filter(VeiculoModel.placa == placa)
            .first()
            is not None
        )

    async def marca_exists(self, marca_id: int) -> bool:
        return self.db.get(MarcaModel, marca_id) is not None

    async def has_ordens_servico(self, veiculo_id: int) -> bool:
        return (
            self.db.query(OrdemServicoModel)
            .filter(OrdemServicoModel.veiculo_id == veiculo_id)
            .first()
            is not None
        )
