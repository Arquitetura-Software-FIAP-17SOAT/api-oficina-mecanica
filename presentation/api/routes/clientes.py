from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from application.commands.create_cliente import (
    CreateClienteCommand,
    CreateClienteUseCase,
)
from application.commands.delete_cliente import (
    DeleteClienteCommand,
    DeleteClienteUseCase,
)
from application.commands.update_cliente import (
    UpdateClienteCommand,
    UpdateClienteUseCase,
)
from application.queries.get_cliente import GetClienteUseCase
from application.queries.list_clientes import ListClientesUseCase
from presentation.api.error_handling import (
    encontrado_ou_404,
    exclusao_ou_404,
    traduzir_value_error,
)
from presentation.api.schemas.clientes import (
    ClienteResponse,
    CreateClienteRequest,
    UpdateClienteRequest,
)
from presentation.dependencies.auth_dependencies import get_current_user
from presentation.dependencies.cliente_dependencies import (
    get_create_cliente_use_case,
    get_delete_cliente_use_case,
    get_get_cliente_use_case,
    get_list_clientes_use_case,
    get_update_cliente_use_case,
)

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    dependencies=[Depends(get_current_user)],
)

CLIENTE_NAO_ENCONTRADO = "Cliente não encontrado."


@router.post(
    "",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar cliente",
    description="Cria um cliente vinculado a um usuário responsável. O CPF/CNPJ não pode se repetir.",
)
async def create_cliente(
    request: CreateClienteRequest,
    use_case: CreateClienteUseCase = Depends(get_create_cliente_use_case),
):
    with traduzir_value_error():
        command = CreateClienteCommand(
            nome=request.nome,
            usuario_id=request.usuario_id,
            cpf_cnpj=request.cpf_cnpj,
            email=request.email,
        )

        return await use_case.execute(command)


@router.get(
    "",
    response_model=list[ClienteResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar clientes",
    description="Lista todos os clientes em ordem alfabética.",
)
async def list_clientes(
    use_case: ListClientesUseCase = Depends(get_list_clientes_use_case),
):
    return await use_case.execute()


@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar cliente",
    description="Retorna um cliente pelo identificador. Devolve 404 se não existir.",
)
async def get_cliente(
    cliente_id: Annotated[
        int, Path(description="Identificador do cliente.", examples=[1])
    ],
    use_case: GetClienteUseCase = Depends(get_get_cliente_use_case),
):
    cliente = await use_case.execute(cliente_id)

    return encontrado_ou_404(cliente, CLIENTE_NAO_ENCONTRADO)


@router.put(
    "/{cliente_id}",
    response_model=ClienteResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar cliente",
    description="Altera nome, CPF/CNPJ e e-mail. Não transfere o cliente para outro usuário.",
)
async def update_cliente(
    cliente_id: Annotated[
        int, Path(description="Identificador do cliente.", examples=[1])
    ],
    request: UpdateClienteRequest,
    use_case: UpdateClienteUseCase = Depends(get_update_cliente_use_case),
):
    with traduzir_value_error():
        command = UpdateClienteCommand(
            cliente_id=cliente_id,
            nome=request.nome,
            cpf_cnpj=request.cpf_cnpj,
            email=request.email,
        )

        cliente = await use_case.execute(command)

    return encontrado_ou_404(cliente, CLIENTE_NAO_ENCONTRADO)


@router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir cliente",
    description="Remove o cliente. Devolve 400 se ele possuir veículos cadastrados.",
)
async def delete_cliente(
    cliente_id: Annotated[
        int, Path(description="Identificador do cliente.", examples=[1])
    ],
    use_case: DeleteClienteUseCase = Depends(get_delete_cliente_use_case),
):
    with traduzir_value_error():
        excluido = await use_case.execute(
            DeleteClienteCommand(cliente_id=cliente_id)
        )

    exclusao_ou_404(excluido, CLIENTE_NAO_ENCONTRADO)
