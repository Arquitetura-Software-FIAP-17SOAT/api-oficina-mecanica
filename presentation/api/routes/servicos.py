from typing import Annotated

from fastapi import APIRouter, Depends, Path, status


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
from presentation.api.error_handling import (
    encontrado_ou_404,
    exclusao_ou_404,
    traduzir_value_error,
)
from presentation.api.schemas.servicos import ServicoRequest, ServicoResponse
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
    with traduzir_value_error():
        command = CreateServicoCommand(
            nome=request.nome,
            valor=request.valor,
            descricao=request.descricao,
            tempo_estimado=request.tempo_estimado,
        )

        return await use_case.execute(command)


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

    return encontrado_ou_404(servico, SERVICO_NAO_ENCONTRADO)


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
    with traduzir_value_error():
        command = UpdateServicoCommand(
            servico_id=servico_id,
            nome=request.nome,
            valor=request.valor,
            descricao=request.descricao,
            tempo_estimado=request.tempo_estimado,
        )

        servico = await use_case.execute(command)

    return encontrado_ou_404(servico, SERVICO_NAO_ENCONTRADO)


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
    with traduzir_value_error():
        excluido = await use_case.execute(
            DeleteServicoCommand(servico_id=servico_id)
        )

    exclusao_ou_404(excluido, SERVICO_NAO_ENCONTRADO)
