from fastapi import Depends

from application.commands.create_servico import CreateServicoUseCase
from application.commands.delete_servico import DeleteServicoUseCase
from application.commands.update_servico import UpdateServicoUseCase
from application.queries.get_servico import GetServicoUseCase
from application.queries.list_servicos import ListServicosUseCase
from infrastructure.database.database import get_db
from domain.repositories.servico_repository_impl import (
    ServicoRepositoryImpl,
)


def get_create_servico_use_case(db=Depends(get_db)) -> CreateServicoUseCase:
    return CreateServicoUseCase(ServicoRepositoryImpl(db))


def get_update_servico_use_case(db=Depends(get_db)) -> UpdateServicoUseCase:
    return UpdateServicoUseCase(ServicoRepositoryImpl(db))


def get_delete_servico_use_case(db=Depends(get_db)) -> DeleteServicoUseCase:
    return DeleteServicoUseCase(ServicoRepositoryImpl(db))


def get_get_servico_use_case(db=Depends(get_db)) -> GetServicoUseCase:
    return GetServicoUseCase(ServicoRepositoryImpl(db))


def get_list_servicos_use_case(db=Depends(get_db)) -> ListServicosUseCase:
    return ListServicosUseCase(ServicoRepositoryImpl(db))
