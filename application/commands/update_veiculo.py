from dataclasses import dataclass

from domain.entities.veiculo import Veiculo
from domain.repositories.veiculo_repository import VeiculoRepository


@dataclass
class UpdateVeiculoCommand:
    """Comando para atualização de veículo."""

    veiculo_id: int
    marca_id: int
    placa: str
    modelo: str
    chassi: str | None = None
    ano_fabricacao: int | None = None


class UpdateVeiculoUseCase:
    """Caso de uso para atualização de veículos."""

    def __init__(self, veiculo_repository: VeiculoRepository):
        self.veiculo_repository = veiculo_repository

    async def execute(self, command: UpdateVeiculoCommand) -> Veiculo | None:
        veiculo = await self.veiculo_repository.find_by_id(command.veiculo_id)

        if veiculo is None:
            return None

        placa_anterior = veiculo.placa

        veiculo.change_marca(command.marca_id)
        veiculo.change_placa(command.placa)
        veiculo.change_modelo(command.modelo)
        veiculo.change_chassi(command.chassi)
        veiculo.change_ano_fabricacao(command.ano_fabricacao)

        if not await self.veiculo_repository.marca_exists(veiculo.marca_id):
            raise ValueError("Marca não encontrada.")

        if veiculo.placa != placa_anterior:
            if await self.veiculo_repository.exists_by_placa(str(veiculo.placa)):
                raise ValueError(
                    "Já existe um veículo cadastrado com essa placa."
                )

        return await self.veiculo_repository.update(veiculo)
