from dataclasses import dataclass

from domain.entities.cliente import Cliente
from domain.repositories.cliente_repository import ClienteRepository


@dataclass
class UpdateClienteCommand:
    """Comando para atualização de cliente."""

    cliente_id: int
    nome: str
    cpf_cnpj: str | None = None
    email: str | None = None


class UpdateClienteUseCase:
    """Caso de uso para atualização de clientes."""

    def __init__(self, cliente_repository: ClienteRepository):
        self.cliente_repository = cliente_repository

    async def execute(self, command: UpdateClienteCommand) -> Cliente | None:
        cliente = await self.cliente_repository.find_by_id(command.cliente_id)

        if cliente is None:
            return None

        cpf_cnpj_anterior = cliente.cpf_cnpj

        cliente.change_nome(command.nome)
        cliente.change_cpf_cnpj(command.cpf_cnpj)
        cliente.change_email(command.email)

        if cliente.cpf_cnpj and cliente.cpf_cnpj != cpf_cnpj_anterior:
            if await self.cliente_repository.exists_by_cpf_cnpj(
                str(cliente.cpf_cnpj)
            ):
                raise ValueError(
                    "Já existe um cliente cadastrado com esse CPF/CNPJ."
                )

        return await self.cliente_repository.update(cliente)
