from fastapi import Depends

from application.commands.create_veiculo import CreateVeiculoUseCase
from application.commands.delete_veiculo import DeleteVeiculoUseCase
from application.commands.update_veiculo import UpdateVeiculoUseCase
from application.queries.get_veiculo import GetVeiculoUseCase
from application.queries.list_veiculos import ListVeiculosUseCase
from infrastructure.database.database import get_db
from infrastructure.database.repositories.cliente_repository_impl import (
    ClienteRepositoryImpl,
)
from infrastructure.database.repositories.veiculo_repository_impl import (
    VeiculoRepositoryImpl,
)


def get_create_veiculo_use_case(db=Depends(get_db)) -> CreateVeiculoUseCase:
    return CreateVeiculoUseCase(
        veiculo_repository=VeiculoRepositoryImpl(db),
        cliente_repository=ClienteRepositoryImpl(db),
    )


def get_update_veiculo_use_case(db=Depends(get_db)) -> UpdateVeiculoUseCase:
    return UpdateVeiculoUseCase(VeiculoRepositoryImpl(db))


def get_delete_veiculo_use_case(db=Depends(get_db)) -> DeleteVeiculoUseCase:
    return DeleteVeiculoUseCase(VeiculoRepositoryImpl(db))


def get_get_veiculo_use_case(db=Depends(get_db)) -> GetVeiculoUseCase:
    return GetVeiculoUseCase(VeiculoRepositoryImpl(db))


def get_list_veiculos_use_case(db=Depends(get_db)) -> ListVeiculosUseCase:
    return ListVeiculosUseCase(VeiculoRepositoryImpl(db))
