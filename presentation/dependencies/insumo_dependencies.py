from fastapi import Depends

from application.commands.add_estoque import AddEstoqueUseCase
from application.commands.adjust_estoque import AdjustEstoqueUseCase
from application.commands.create_insumo import CreateInsumoUseCase
from application.commands.delete_insumo import DeleteInsumoUseCase
from application.commands.remove_estoque import RemoveEstoqueUseCase
from application.commands.update_insumo import UpdateInsumoUseCase
from application.queries.get_insumo import GetInsumoUseCase
from application.queries.list_insumos import ListInsumosUseCase
from application.queries.list_insumos_estoque_baixo import (
    ListInsumosEstoqueBaixoUseCase,
)
from infrastructure.database.database import get_db
from infrastructure.database.repositories.insumo_repository_impl import (
    InsumoRepositoryImpl,
)


def get_create_insumo_use_case(db=Depends(get_db)) -> CreateInsumoUseCase:
    return CreateInsumoUseCase(InsumoRepositoryImpl(db))


def get_update_insumo_use_case(db=Depends(get_db)) -> UpdateInsumoUseCase:
    return UpdateInsumoUseCase(InsumoRepositoryImpl(db))


def get_delete_insumo_use_case(db=Depends(get_db)) -> DeleteInsumoUseCase:
    return DeleteInsumoUseCase(InsumoRepositoryImpl(db))


def get_add_estoque_use_case(db=Depends(get_db)) -> AddEstoqueUseCase:
    return AddEstoqueUseCase(InsumoRepositoryImpl(db))


def get_remove_estoque_use_case(db=Depends(get_db)) -> RemoveEstoqueUseCase:
    return RemoveEstoqueUseCase(InsumoRepositoryImpl(db))


def get_adjust_estoque_use_case(db=Depends(get_db)) -> AdjustEstoqueUseCase:
    return AdjustEstoqueUseCase(InsumoRepositoryImpl(db))


def get_get_insumo_use_case(db=Depends(get_db)) -> GetInsumoUseCase:
    return GetInsumoUseCase(InsumoRepositoryImpl(db))


def get_list_insumos_use_case(db=Depends(get_db)) -> ListInsumosUseCase:
    return ListInsumosUseCase(InsumoRepositoryImpl(db))


def get_list_insumos_estoque_baixo_use_case(
    db=Depends(get_db),
) -> ListInsumosEstoqueBaixoUseCase:
    return ListInsumosEstoqueBaixoUseCase(InsumoRepositoryImpl(db))
