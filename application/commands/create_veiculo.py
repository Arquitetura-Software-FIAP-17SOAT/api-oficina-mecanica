from dataclasses import dataclass

from domain.entities.veiculo import Veiculo
from domain.repositories.cliente_repository import ClienteRepository
from domain.repositories.veiculo_repository import VeiculoRepository


@dataclass
class CreateVeiculoCommand:
    cliente_id: int
    marca_id: int
    placa: str
    modelo: str
    chassi: str | None = None
    ano_fabricacao: int | None = None


class CreateVeiculoUseCase:
    def __init__(
        self,
        veiculo_repository: VeiculoRepository,
        cliente_repository: ClienteRepository,
    ):
        self.veiculo_repository = veiculo_repository
        self.cliente_repository = cliente_repository

    async def execute(self, command: CreateVeiculoCommand) -> Veiculo:
        veiculo = Veiculo(
            cliente_id=command.cliente_id,
            marca_id=command.marca_id,
            placa=command.placa,
            modelo=command.modelo,
            chassi=command.chassi,
            ano_fabricacao=command.ano_fabricacao,
        )

        if await self.cliente_repository.find_by_id(veiculo.cliente_id) is None:
            raise ValueError("Cliente não encontrado.")

        if not await self.veiculo_repository.marca_exists(veiculo.marca_id):
            raise ValueError("Marca não encontrada.")

        if await self.veiculo_repository.exists_by_placa(str(veiculo.placa)):
            raise ValueError("Já existe um veículo cadastrado com essa placa.")

        return await self.veiculo_repository.save(veiculo)
