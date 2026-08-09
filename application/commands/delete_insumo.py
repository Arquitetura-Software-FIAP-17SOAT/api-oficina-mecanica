from dataclasses import dataclass

from domain.repositories.insumo_repository import InsumoRepository


@dataclass
class DeleteInsumoCommand:
    insumo_id: int


class DeleteInsumoUseCase:
    def __init__(self, insumo_repository: InsumoRepository):
        self.insumo_repository = insumo_repository

    async def execute(self, command: DeleteInsumoCommand) -> bool:
        insumo = await self.insumo_repository.find_by_id(command.insumo_id)

        if insumo is None:
            return False

        if await self.insumo_repository.has_vinculos(command.insumo_id):
            raise ValueError(
                "O insumo não pode ser excluído porque está vinculado a um "
                "ou mais serviços."
            )

        await self.insumo_repository.delete(command.insumo_id)

        return True
