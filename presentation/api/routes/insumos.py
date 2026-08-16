from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

from domain.value_objects.dinheiro import Dinheiro

from application.commands.add_estoque import AddEstoqueCommand, AddEstoqueUseCase
from application.commands.adjust_estoque import (
    AdjustEstoqueCommand,
    AdjustEstoqueUseCase,
)
from application.commands.create_insumo import (
    CreateInsumoCommand,
    CreateInsumoUseCase,
)
from application.commands.delete_insumo import (
    DeleteInsumoCommand,
    DeleteInsumoUseCase,
)
from application.commands.remove_estoque import (
    RemoveEstoqueCommand,
    RemoveEstoqueUseCase,
)
from application.commands.update_insumo import (
    UpdateInsumoCommand,
    UpdateInsumoUseCase,
)
from application.queries.get_insumo import GetInsumoUseCase
from application.queries.list_insumos import ListInsumosUseCase
from application.queries.list_insumos_estoque_baixo import (
    ListInsumosEstoqueBaixoUseCase,
)
from presentation.dependencies.auth_dependencies import get_current_user
from presentation.dependencies.insumo_dependencies import (
    get_add_estoque_use_case,
    get_adjust_estoque_use_case,
    get_create_insumo_use_case,
    get_delete_insumo_use_case,
    get_get_insumo_use_case,
    get_list_insumos_estoque_baixo_use_case,
    get_list_insumos_use_case,
    get_remove_estoque_use_case,
    get_update_insumo_use_case,
)

router = APIRouter(
    prefix="/insumos",
    tags=["Insumos"],
    dependencies=[Depends(get_current_user)],
)

INSUMO_NAO_ENCONTRADO = "Insumo não encontrado."


class CreateInsumoRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Óleo 5W30",
                "descricao": "Óleo sintético, embalagem de 1 litro",
                "preco_unitario": "45.90",
                "estoque": 10,
                "quantidade_minima": 3,
            }
        }
    )

    nome: str = Field(
        description="Nome da peça ou insumo. Máximo de 120 caracteres.",
        examples=["Óleo 5W30"],
    )
    descricao: str | None = Field(
        default=None,
        description="Detalhamento livre. Opcional.",
        examples=["Óleo sintético, embalagem de 1 litro"],
    )
    preco_unitario: Decimal | None = Field(
        default=None,
        description=(
            "Preço de custo unitário, com até 2 casas decimais. "
            "Aceita número ou texto. Opcional."
        ),
        examples=["45.90"],
    )
    estoque: int = Field(
        default=0,
        description="Saldo inicial em estoque. Não pode ser negativo.",
        examples=[10],
    )
    quantidade_minima: int = Field(
        default=0,
        description=(
            "Saldo mínimo desejado. Quando o estoque atinge ou fica abaixo "
            "deste valor, o insumo passa a aparecer em GET /insumos/estoque-baixo."
        ),
        examples=[3],
    )


class UpdateInsumoRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Óleo 5W30",
                "descricao": "Óleo sintético, embalagem de 1 litro",
                "preco_unitario": "49.90",
                "quantidade_minima": 5,
            }
        }
    )

    nome: str = Field(
        description="Nome da peça ou insumo. Máximo de 120 caracteres.",
        examples=["Óleo 5W30"],
    )
    descricao: str | None = Field(
        default=None,
        description="Detalhamento livre. Opcional.",
        examples=["Óleo sintético, embalagem de 1 litro"],
    )
    preco_unitario: Decimal | None = Field(
        default=None,
        description="Preço de custo unitário, com até 2 casas decimais. Opcional.",
        examples=["49.90"],
    )
    quantidade_minima: int = Field(
        default=0,
        description="Saldo mínimo desejado para alerta de reposição.",
        examples=[5],
    )


class MovimentacaoEstoqueRequest(BaseModel):
    """Quantidade a somar ou subtrair do saldo atual."""

    model_config = ConfigDict(json_schema_extra={"example": {"quantidade": 5}})

    quantidade: int = Field(
        description=(
            "Quantidade movimentada, sempre positiva. "
            "É somada ou subtraída do saldo atual, não o substitui."
        ),
        examples=[5],
    )


class AjusteEstoqueRequest(BaseModel):
    """Novo saldo absoluto, apurado em contagem física."""

    model_config = ConfigDict(json_schema_extra={"example": {"quantidade": 8}})

    quantidade: int = Field(
        description=(
            "Novo saldo total do insumo, substituindo o valor atual. "
            "Aceita zero. Não pode ser negativo."
        ),
        examples=[8],
    )


class InsumoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: str | None
    preco_unitario: Decimal | None
    estoque: int
    quantidade_minima: int
    estoque_baixo: bool

    @field_validator("preco_unitario", mode="before")
    @classmethod
    def _preco_para_decimal(cls, valor):
        return valor.value if isinstance(valor, Dinheiro) else valor


@router.post(
    "",
    response_model=InsumoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar insumo",
    description="Cria uma peça ou insumo. O nome não pode se repetir.",
)
async def create_insumo(
    request: CreateInsumoRequest,
    use_case: CreateInsumoUseCase = Depends(get_create_insumo_use_case),
):
    try:
        command = CreateInsumoCommand(
            nome=request.nome,
            descricao=request.descricao,
            preco_unitario=request.preco_unitario,
            estoque=request.estoque,
            quantidade_minima=request.quantidade_minima,
        )

        return await use_case.execute(command)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=list[InsumoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar insumos",
    description="Lista todos os insumos em ordem alfabética.",
)
async def list_insumos(
    use_case: ListInsumosUseCase = Depends(get_list_insumos_use_case),
):
    return await use_case.execute()


@router.get(
    "/estoque-baixo",
    response_model=list[InsumoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar insumos que precisam de reposição",
    description="Retorna os insumos cujo estoque atingiu ou ficou abaixo da quantidade mínima.",
)
async def list_insumos_estoque_baixo(
    use_case: ListInsumosEstoqueBaixoUseCase = Depends(
        get_list_insumos_estoque_baixo_use_case
    ),
):
    return await use_case.execute()


@router.get(
    "/{insumo_id}",
    response_model=InsumoResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar insumo",
    description="Retorna um insumo pelo identificador. Devolve 404 se não existir.",
)
async def get_insumo(
    insumo_id: Annotated[
        int, Path(description="Identificador do insumo.", examples=[1])
    ],
    use_case: GetInsumoUseCase = Depends(get_get_insumo_use_case),
):
    insumo = await use_case.execute(insumo_id)

    if insumo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=INSUMO_NAO_ENCONTRADO,
        )

    return insumo


@router.put(
    "/{insumo_id}",
    response_model=InsumoResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar cadastro do insumo",
    description="Altera nome, descrição, preço e quantidade mínima. Não altera o saldo em estoque.",
)
async def update_insumo(
    insumo_id: Annotated[
        int, Path(description="Identificador do insumo.", examples=[1])
    ],
    request: UpdateInsumoRequest,
    use_case: UpdateInsumoUseCase = Depends(get_update_insumo_use_case),
):
    try:
        command = UpdateInsumoCommand(
            insumo_id=insumo_id,
            nome=request.nome,
            descricao=request.descricao,
            preco_unitario=request.preco_unitario,
            quantidade_minima=request.quantidade_minima,
        )

        insumo = await use_case.execute(command)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if insumo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=INSUMO_NAO_ENCONTRADO,
        )

    return insumo


@router.delete(
    "/{insumo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir insumo",
    description="Remove o insumo. Devolve 400 se ele estiver vinculado a algum serviço.",
)
async def delete_insumo(
    insumo_id: Annotated[
        int, Path(description="Identificador do insumo.", examples=[1])
    ],
    use_case: DeleteInsumoUseCase = Depends(get_delete_insumo_use_case),
):
    try:
        excluido = await use_case.execute(DeleteInsumoCommand(insumo_id=insumo_id))

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not excluido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=INSUMO_NAO_ENCONTRADO,
        )


@router.post(
    "/{insumo_id}/estoque/entrada",
    response_model=InsumoResponse,
    status_code=status.HTTP_200_OK,
    summary="Registrar entrada de estoque",
    description="Soma a quantidade informada ao saldo atual. Use para compras e devoluções.",
)
async def registrar_entrada_estoque(
    insumo_id: Annotated[
        int, Path(description="Identificador do insumo.", examples=[1])
    ],
    request: MovimentacaoEstoqueRequest,
    use_case: AddEstoqueUseCase = Depends(get_add_estoque_use_case),
):
    try:
        command = AddEstoqueCommand(
            insumo_id=insumo_id,
            quantidade=request.quantidade,
        )

        insumo = await use_case.execute(command)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if insumo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=INSUMO_NAO_ENCONTRADO,
        )

    return insumo


@router.post(
    "/{insumo_id}/estoque/saida",
    response_model=InsumoResponse,
    status_code=status.HTTP_200_OK,
    summary="Registrar saída de estoque",
    description="Subtrai a quantidade do saldo atual. Devolve 400 se o saldo for insuficiente.",
)
async def registrar_saida_estoque(
    insumo_id: Annotated[
        int, Path(description="Identificador do insumo.", examples=[1])
    ],
    request: MovimentacaoEstoqueRequest,
    use_case: RemoveEstoqueUseCase = Depends(get_remove_estoque_use_case),
):
    try:
        command = RemoveEstoqueCommand(
            insumo_id=insumo_id,
            quantidade=request.quantidade,
        )

        insumo = await use_case.execute(command)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if insumo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=INSUMO_NAO_ENCONTRADO,
        )

    return insumo


@router.post(
    "/{insumo_id}/estoque/ajuste",
    response_model=InsumoResponse,
    status_code=status.HTTP_200_OK,
    summary="Ajustar saldo por contagem física",
    description="Substitui o saldo pelo valor informado. Aceita zero.",
)
async def ajustar_estoque(
    insumo_id: Annotated[
        int, Path(description="Identificador do insumo.", examples=[1])
    ],
    request: AjusteEstoqueRequest,
    use_case: AdjustEstoqueUseCase = Depends(get_adjust_estoque_use_case),
):
    try:
        command = AdjustEstoqueCommand(
            insumo_id=insumo_id,
            quantidade=request.quantidade,
        )

        insumo = await use_case.execute(command)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if insumo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=INSUMO_NAO_ENCONTRADO,
        )

    return insumo
