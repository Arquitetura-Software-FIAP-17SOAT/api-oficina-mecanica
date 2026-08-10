from dataclasses import dataclass

from domain.repositories.cliente_repository import ClienteRepository


@dataclass
class DeleteClienteCommand:
    cliente_id: int


class DeleteClienteUseCase:
    def __init__(self, cliente_repository: ClienteRepository):
        self.cliente_repository = cliente_repository

    async def execute(self, command: DeleteClienteCommand) -> bool:
        cliente = await self.cliente_repository.find_by_id(command.cliente_id)

        if cliente is None:
            return False

        if await self.cliente_repository.has_veiculos(command.cliente_id):
            raise ValueError(
                "O cliente não pode ser excluído porque possui veículos "
                "cadastrados."
            )

        await self.cliente_repository.delete(command.cliente_id)

        return True
