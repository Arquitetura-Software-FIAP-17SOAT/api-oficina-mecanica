from __future__ import annotations

from sqlalchemy.orm import Session

from domain.entities.cliente import Cliente
from domain.repositories.cliente_repository import ClienteRepository
from infrastructure.database.models import ClienteModel, VeiculoModel


class ClienteRepositoryImpl(ClienteRepository):
    """Persistência de clientes."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_entity(model: ClienteModel) -> Cliente:
        return Cliente(
            id=model.id,
            nome=model.nome,
            usuario_id=model.usuario_id,
            cpf_cnpj=model.cpf_cnpj,
            email=model.email,
        )

    async def save(self, cliente: Cliente) -> Cliente:
        model = ClienteModel(
            usuario_id=cliente.usuario_id,
            nome=cliente.nome,
            cpf_cnpj=str(cliente.cpf_cnpj) if cliente.cpf_cnpj else None,
            email=str(cliente.email) if cliente.email else None,
        )

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        cliente.id = model.id

        return cliente

    async def find_by_id(self, cliente_id: int) -> Cliente | None:
        model = self.db.get(ClienteModel, cliente_id)

        return self._to_entity(model) if model else None

    async def list(self) -> list[Cliente]:
        models = (
            self.db.query(ClienteModel)
            .order_by(ClienteModel.nome)
            .all()
        )

        return [self._to_entity(model) for model in models]

    async def update(self, cliente: Cliente) -> Cliente:
        model = self.db.get(ClienteModel, cliente.id)

        if model is None:
            raise ValueError("Cliente não encontrado.")

        model.nome = cliente.nome
        model.cpf_cnpj = str(cliente.cpf_cnpj) if cliente.cpf_cnpj else None
        model.email = str(cliente.email) if cliente.email else None

        self.db.commit()

        return cliente

    async def delete(self, cliente_id: int) -> None:
        model = self.db.get(ClienteModel, cliente_id)

        if model is None:
            return

        self.db.delete(model)
        self.db.commit()

    async def exists_by_cpf_cnpj(self, cpf_cnpj: str) -> bool:
        return (
            self.db.query(ClienteModel)
            .filter(ClienteModel.cpf_cnpj == cpf_cnpj)
            .first()
            is not None
        )

    async def has_veiculos(self, cliente_id: int) -> bool:
        return (
            self.db.query(VeiculoModel)
            .filter(VeiculoModel.cliente_id == cliente_id)
            .first()
            is not None
        )
