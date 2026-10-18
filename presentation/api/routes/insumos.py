from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

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
from presentation.api.error_handling import (
    encontrado_ou_404,
    exclusao_ou_404,
    traduzir_value_error,
)
from presentation.api.schemas.insumos import (
    AjusteEstoqueRequest,
    CreateInsumoRequest,
    InsumoResponse,
    MovimentacaoEstoqueRequest,
    UpdateInsumoRequest,
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
    with traduzir_value_error():
        command = CreateInsumoCommand(
            nome=request.nome,
            descricao=request.descricao,
            preco_unitario=request.preco_unitario,
            estoque=request.estoque,
            quantidade_minima=request.quantidade_minima,
        )

        return await use_case.execute(command)


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

    return encontrado_ou_404(insumo, INSUMO_NAO_ENCONTRADO)


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
    with traduzir_value_error():
        command = UpdateInsumoCommand(
            insumo_id=insumo_id,
            nome=request.nome,
            descricao=request.descricao,
            preco_unitario=request.preco_unitario,
            quantidade_minima=request.quantidade_minima,
        )

        insumo = await use_case.execute(command)

    return encontrado_ou_404(insumo, INSUMO_NAO_ENCONTRADO)


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
    with traduzir_value_error():
        excluido = await use_case.execute(DeleteInsumoCommand(insumo_id=insumo_id))

    exclusao_ou_404(excluido, INSUMO_NAO_ENCONTRADO)


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
    with traduzir_value_error():
        command = AddEstoqueCommand(
            insumo_id=insumo_id,
            quantidade=request.quantidade,
        )

        insumo = await use_case.execute(command)

    return encontrado_ou_404(insumo, INSUMO_NAO_ENCONTRADO)


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
    with traduzir_value_error():
        command = RemoveEstoqueCommand(
            insumo_id=insumo_id,
            quantidade=request.quantidade,
        )

        insumo = await use_case.execute(command)

    return encontrado_ou_404(insumo, INSUMO_NAO_ENCONTRADO)


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
    with traduzir_value_error():
        command = AdjustEstoqueCommand(
            insumo_id=insumo_id,
            quantidade=request.quantidade,
        )

        insumo = await use_case.execute(command)

    return encontrado_ou_404(insumo, INSUMO_NAO_ENCONTRADO)
