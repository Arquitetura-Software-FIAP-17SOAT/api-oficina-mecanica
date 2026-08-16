from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

from domain.value_objects.dinheiro import Dinheiro

from application.commands.create_servico import (
    CreateServicoCommand,
    CreateServicoUseCase,
)
from application.commands.delete_servico import (
    DeleteServicoCommand,
    DeleteServicoUseCase,
)
from application.commands.update_servico import (
    UpdateServicoCommand,
    UpdateServicoUseCase,
)
from application.queries.get_servico import GetServicoUseCase
from application.queries.list_servicos import ListServicosUseCase
from presentation.dependencies.auth_dependencies import get_current_user
from presentation.dependencies.servico_dependencies import (
    get_create_servico_use_case,
    get_delete_servico_use_case,
    get_get_servico_use_case,
    get_list_servicos_use_case,
    get_update_servico_use_case,
)

router = APIRouter(
    prefix="/servicos",
    tags=["Serviços"],
    dependencies=[Depends(get_current_user)],
)

SERVICO_NAO_ENCONTRADO = "Serviço não encontrado."


class ServicoRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Troca de óleo",
                "valor": "120.00",
                "descricao": "Inclui óleo sintético e filtro",
                "tempo_estimado": "1h",
            }
        }
    )

    nome: str = Field(
        description="Nome do serviço. Máximo de 100 caracteres, não pode repetir.",
        examples=["Troca de óleo"],
    )
    valor: Decimal = Field(
        description=(
            "Preço cobrado, com até 2 casas decimais. Obrigatório. "
            "Aceita zero para cortesia. Máximo de 99999999.99."
        ),
        examples=["120.00"],
    )
    descricao: str | None = Field(
        default=None,
        description="Detalhamento do que está incluso. Opcional.",
        examples=["Inclui óleo sintético e filtro"],
    )
    tempo_estimado: str | None = Field(
        default=None,
        description=(
            "Duração estimada, em texto livre. Máximo de 30 caracteres. Opcional."
        ),
        examples=["1h", "30min", "2 dias"],
    )


class ServicoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    valor: Decimal
    descricao: str | None
    tempo_estimado: str | None

    @field_validator("valor", mode="before")
    @classmethod
    def _valor_para_decimal(cls, valor):
        return valor.value if isinstance(valor, Dinheiro) else valor


@router.post(
    "",
    response_model=ServicoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar serviço",
    description="Cria um serviço do catálogo. O nome não pode se repetir.",
)
async def create_servico(
    request: ServicoRequest,
    use_case: CreateServicoUseCase = Depends(get_create_servico_use_case),
):
    try:
        command = CreateServicoCommand(
            nome=request.nome,
            valor=request.valor,
            descricao=request.descricao,
            tempo_estimado=request.tempo_estimado,
        )

        return await use_case.execute(command)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=list[ServicoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar serviços",
    description="Lista todos os serviços em ordem alfabética.",
)
async def list_servicos(
    use_case: ListServicosUseCase = Depends(get_list_servicos_use_case),
):
    return await use_case.execute()


@router.get(
    "/{servico_id}",
    response_model=ServicoResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar serviço",
    description="Retorna um serviço pelo identificador. Devolve 404 se não existir.",
)
async def get_servico(
    servico_id: Annotated[
        int, Path(description="Identificador do serviço.", examples=[1])
    ],
    use_case: GetServicoUseCase = Depends(get_get_servico_use_case),
):
    servico = await use_case.execute(servico_id)

    if servico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=SERVICO_NAO_ENCONTRADO,
        )

    return servico


@router.put(
    "/{servico_id}",
    response_model=ServicoResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar serviço",
    description="Altera nome, valor, descrição e tempo estimado.",
)
async def update_servico(
    servico_id: Annotated[
        int, Path(description="Identificador do serviço.", examples=[1])
    ],
    request: ServicoRequest,
    use_case: UpdateServicoUseCase = Depends(get_update_servico_use_case),
):
    try:
        command = UpdateServicoCommand(
            servico_id=servico_id,
            nome=request.nome,
            valor=request.valor,
            descricao=request.descricao,
            tempo_estimado=request.tempo_estimado,
        )

        servico = await use_case.execute(command)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if servico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=SERVICO_NAO_ENCONTRADO,
        )

    return servico


@router.delete(
    "/{servico_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir serviço",
    description="Remove o serviço. Devolve 400 se ele estiver vinculado a insumos ou ordens de serviço.",
)
async def delete_servico(
    servico_id: Annotated[
        int, Path(description="Identificador do serviço.", examples=[1])
    ],
    use_case: DeleteServicoUseCase = Depends(get_delete_servico_use_case),
):
    try:
        excluido = await use_case.execute(
            DeleteServicoCommand(servico_id=servico_id)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not excluido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=SERVICO_NAO_ENCONTRADO,
        )
