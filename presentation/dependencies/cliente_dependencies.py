from fastapi import Depends

from application.commands.create_cliente import CreateClienteUseCase
from application.commands.delete_cliente import DeleteClienteUseCase
from application.commands.update_cliente import UpdateClienteUseCase
from application.queries.get_cliente import GetClienteUseCase
from application.queries.list_clientes import ListClientesUseCase
from infrastructure.database.database import get_db
from infrastructure.database.repositories.cliente_repository_impl import (
    ClienteRepositoryImpl,
)
from infrastructure.database.repositories.user_repository_impl import (
    UserRepositoryImpl,
)


def get_create_cliente_use_case(db=Depends(get_db)) -> CreateClienteUseCase:
    return CreateClienteUseCase(
        cliente_repository=ClienteRepositoryImpl(db),
        user_repository=UserRepositoryImpl(db),
    )


def get_update_cliente_use_case(db=Depends(get_db)) -> UpdateClienteUseCase:
    return UpdateClienteUseCase(ClienteRepositoryImpl(db))


def get_delete_cliente_use_case(db=Depends(get_db)) -> DeleteClienteUseCase:
    return DeleteClienteUseCase(ClienteRepositoryImpl(db))


def get_get_cliente_use_case(db=Depends(get_db)) -> GetClienteUseCase:
    return GetClienteUseCase(ClienteRepositoryImpl(db))


def get_list_clientes_use_case(db=Depends(get_db)) -> ListClientesUseCase:
    return ListClientesUseCase(ClienteRepositoryImpl(db))
