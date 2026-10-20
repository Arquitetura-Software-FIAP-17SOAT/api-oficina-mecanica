from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status


from application.commands.create_veiculo import (
    CreateVeiculoCommand,
    CreateVeiculoUseCase,
)
from application.commands.delete_veiculo import (
    DeleteVeiculoCommand,
    DeleteVeiculoUseCase,
)
from application.commands.update_veiculo import (
    UpdateVeiculoCommand,
    UpdateVeiculoUseCase,
)
from application.queries.get_veiculo import GetVeiculoUseCase
from application.queries.list_veiculos import ListVeiculosUseCase
from presentation.api.error_handling import (
    encontrado_ou_404,
    exclusao_ou_404,
    traduzir_value_error,
)
from presentation.api.schemas.veiculos import (
    CreateVeiculoRequest,
    UpdateVeiculoRequest,
    VeiculoResponse,
)
from presentation.dependencies.auth_dependencies import get_current_user
from presentation.dependencies.veiculo_dependencies import (
    get_create_veiculo_use_case,
    get_delete_veiculo_use_case,
    get_get_veiculo_use_case,
    get_list_veiculos_use_case,
    get_update_veiculo_use_case,
)

router = APIRouter(
    prefix="/veiculos",
    tags=["Veículos"],
    dependencies=[Depends(get_current_user)],
)

VEICULO_NAO_ENCONTRADO = "Veículo não encontrado."


@router.post(
    "",
    response_model=VeiculoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar veículo",
    description="Cria um veículo para um cliente. A placa não pode se repetir.",
)
async def create_veiculo(
    request: CreateVeiculoRequest,
    use_case: CreateVeiculoUseCase = Depends(get_create_veiculo_use_case),
):
    with traduzir_value_error():
        command = CreateVeiculoCommand(
            cliente_id=request.cliente_id,
            marca_id=request.marca_id,
            placa=request.placa,
            modelo=request.modelo,
            chassi=request.chassi,
            ano_fabricacao=request.ano_fabricacao,
        )

        return await use_case.execute(command)


@router.get(
    "",
    response_model=list[VeiculoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar veículos",
    description="Lista os veículos em ordem de placa. Aceita filtro por cliente.",
)
async def list_veiculos(
    cliente_id: Annotated[
        int | None,
        Query(
            description=(
                "Filtra os veículos de um cliente específico. "
                "Omita para listar todos."
            ),
            examples=[1],
        ),
    ] = None,
    use_case: ListVeiculosUseCase = Depends(get_list_veiculos_use_case),
):
    return await use_case.execute(cliente_id=cliente_id)


@router.get(
    "/{veiculo_id}",
    response_model=VeiculoResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar veículo",
    description="Retorna um veículo pelo identificador. Devolve 404 se não existir.",
)
async def get_veiculo(
    veiculo_id: Annotated[
        int, Path(description="Identificador do veículo.", examples=[1])
    ],
    use_case: GetVeiculoUseCase = Depends(get_get_veiculo_use_case),
):
    veiculo = await use_case.execute(veiculo_id)

    return encontrado_ou_404(veiculo, VEICULO_NAO_ENCONTRADO)


@router.put(
    "/{veiculo_id}",
    response_model=VeiculoResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar veículo",
    description="Altera marca, placa, modelo, chassi e ano. Não transfere o veículo para outro cliente.",
)
async def update_veiculo(
    veiculo_id: Annotated[
        int, Path(description="Identificador do veículo.", examples=[1])
    ],
    request: UpdateVeiculoRequest,
    use_case: UpdateVeiculoUseCase = Depends(get_update_veiculo_use_case),
):
    with traduzir_value_error():
        command = UpdateVeiculoCommand(
            veiculo_id=veiculo_id,
            marca_id=request.marca_id,
            placa=request.placa,
            modelo=request.modelo,
            chassi=request.chassi,
            ano_fabricacao=request.ano_fabricacao,
        )

        veiculo = await use_case.execute(command)

    return encontrado_ou_404(veiculo, VEICULO_NAO_ENCONTRADO)


@router.delete(
    "/{veiculo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir veículo",
    description="Remove o veículo. Devolve 400 se ele possuir ordens de serviço.",
)
async def delete_veiculo(
    veiculo_id: Annotated[
        int, Path(description="Identificador do veículo.", examples=[1])
    ],
    use_case: DeleteVeiculoUseCase = Depends(get_delete_veiculo_use_case),
):
    with traduzir_value_error():
        excluido = await use_case.execute(
            DeleteVeiculoCommand(veiculo_id=veiculo_id)
        )

    exclusao_ou_404(excluido, VEICULO_NAO_ENCONTRADO)
