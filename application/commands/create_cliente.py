from dataclasses import dataclass

from domain.entities.cliente import Cliente
from domain.repositories.cliente_repository import ClienteRepository
from domain.repositories.user_repository import UserRepository


@dataclass
class CreateClienteCommand:
    nome: str
    usuario_id: int
    cpf_cnpj: str | None = None
    email: str | None = None


class CreateClienteUseCase:
    def __init__(
        self,
        cliente_repository: ClienteRepository,
        user_repository: UserRepository,
    ):
        self.cliente_repository = cliente_repository
        self.user_repository = user_repository

    async def execute(self, command: CreateClienteCommand) -> Cliente:
        cliente = Cliente(
            nome=command.nome,
            usuario_id=command.usuario_id,
            cpf_cnpj=command.cpf_cnpj,
            email=command.email,
        )

        if await self.user_repository.find_by_id(cliente.usuario_id) is None:
            raise ValueError("Usuário responsável não encontrado.")

        if cliente.cpf_cnpj and await self.cliente_repository.exists_by_cpf_cnpj(
            str(cliente.cpf_cnpj)
        ):
            raise ValueError("Já existe um cliente cadastrado com esse CPF/CNPJ.")

        return await self.cliente_repository.save(cliente)
