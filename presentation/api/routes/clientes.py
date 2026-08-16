from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

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


CPF_CNPJ_DESCRICAO = (
    "CPF (11 dígitos) ou CNPJ (14 dígitos). Aceita com ou sem máscara — "
    "é armazenado só com os dígitos. Validado pelo dígito verificador. Opcional."
)
EMAIL_DESCRICAO = "E-mail de contato. Máximo de 150 caracteres. Opcional."
NOME_DESCRICAO = "Nome ou razão social do cliente. Máximo de 150 caracteres."


class CreateClienteRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Maria Souza",
                "usuario_id": 1,
                "cpf_cnpj": "529.982.247-25",
                "email": "maria@example.com",
            }
        }
    )

    nome: str = Field(description=NOME_DESCRICAO, examples=["Maria Souza"])
    usuario_id: int = Field(
        description=(
            "Identificador do usuário responsável pelo cliente. "
            "Precisa existir em /users."
        ),
        examples=[1],
    )
    cpf_cnpj: str | None = Field(
        default=None,
        description=CPF_CNPJ_DESCRICAO,
        examples=["529.982.247-25"],
    )
    email: str | None = Field(
        default=None,
        description=EMAIL_DESCRICAO,
        examples=["maria@example.com"],
    )


class UpdateClienteRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Maria Souza Lima",
                "cpf_cnpj": "529.982.247-25",
                "email": "maria.lima@example.com",
            }
        }
    )

    nome: str = Field(description=NOME_DESCRICAO, examples=["Maria Souza Lima"])
    cpf_cnpj: str | None = Field(
        default=None,
        description=CPF_CNPJ_DESCRICAO,
        examples=["529.982.247-25"],
    )
    email: str | None = Field(
        default=None,
        description=EMAIL_DESCRICAO,
        examples=["maria.lima@example.com"],
    )


class ClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    usuario_id: int
    cpf_cnpj: str | None
    email: str | None

    @field_validator("cpf_cnpj", "email", mode="before")
    @classmethod
    def _value_object_para_texto(cls, valor):
        return str(valor) if valor is not None else None


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
    try:
        command = CreateClienteCommand(
            nome=request.nome,
            usuario_id=request.usuario_id,
            cpf_cnpj=request.cpf_cnpj,
            email=request.email,
        )

        return await use_case.execute(command)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


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

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CLIENTE_NAO_ENCONTRADO,
        )

    return cliente


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
    try:
        command = UpdateClienteCommand(
            cliente_id=cliente_id,
            nome=request.nome,
            cpf_cnpj=request.cpf_cnpj,
            email=request.email,
        )

        cliente = await use_case.execute(command)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CLIENTE_NAO_ENCONTRADO,
        )

    return cliente


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
    try:
        excluido = await use_case.execute(
            DeleteClienteCommand(cliente_id=cliente_id)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not excluido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CLIENTE_NAO_ENCONTRADO,
        )
