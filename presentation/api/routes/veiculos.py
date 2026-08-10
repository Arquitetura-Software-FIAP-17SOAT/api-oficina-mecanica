from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

from domain.value_objects.data_hora import DataHora

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
)

VEICULO_NAO_ENCONTRADO = "Veículo não encontrado."


PLACA_DESCRICAO = (
    "Placa no formato antigo (ABC1234) ou Mercosul (ABC1D23). "
    "Hífen e espaços são removidos e a placa é gravada em maiúsculas."
)
MARCA_DESCRICAO = (
    "Identificador da marca. Precisa existir na tabela `marcas`, "
    "que hoje é populada por SQL — não há endpoint de cadastro."
)
MODELO_DESCRICAO = "Modelo do veículo. Máximo de 100 caracteres."
CHASSI_DESCRICAO = "Número do chassi. Máximo de 30 caracteres. Opcional."
ANO_DESCRICAO = (
    "Ano de fabricação, entre 1900 e o ano seguinte ao atual. Opcional."
)


class CreateVeiculoRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cliente_id": 1,
                "marca_id": 1,
                "placa": "ABC1D23",
                "modelo": "Gol 1.0",
                "chassi": "9BWZZZ377VT004251",
                "ano_fabricacao": 2020,
            }
        }
    )

    cliente_id: int = Field(
        description="Identificador do cliente dono do veículo. Precisa existir.",
        examples=[1],
    )
    marca_id: int = Field(description=MARCA_DESCRICAO, examples=[1])
    placa: str = Field(description=PLACA_DESCRICAO, examples=["ABC1D23"])
    modelo: str = Field(description=MODELO_DESCRICAO, examples=["Gol 1.0"])
    chassi: str | None = Field(
        default=None,
        description=CHASSI_DESCRICAO,
        examples=["9BWZZZ377VT004251"],
    )
    ano_fabricacao: int | None = Field(
        default=None, description=ANO_DESCRICAO, examples=[2020]
    )


class UpdateVeiculoRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "marca_id": 1,
                "placa": "ABC1D23",
                "modelo": "Gol 1.6",
                "chassi": "9BWZZZ377VT004251",
                "ano_fabricacao": 2021,
            }
        }
    )

    marca_id: int = Field(description=MARCA_DESCRICAO, examples=[1])
    placa: str = Field(description=PLACA_DESCRICAO, examples=["ABC1D23"])
    modelo: str = Field(description=MODELO_DESCRICAO, examples=["Gol 1.6"])
    chassi: str | None = Field(
        default=None,
        description=CHASSI_DESCRICAO,
        examples=["9BWZZZ377VT004251"],
    )
    ano_fabricacao: int | None = Field(
        default=None, description=ANO_DESCRICAO, examples=[2021]
    )


class VeiculoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    marca_id: int
    placa: str
    modelo: str
    chassi: str | None
    ano_fabricacao: int | None
    criado_em: datetime | None

    @field_validator("criado_em", mode="before")
    @classmethod
    def _data_para_datetime(cls, valor):
        return valor.value if isinstance(valor, DataHora) else valor

    @field_validator("placa", "chassi", mode="before")
    @classmethod
    def _value_object_para_texto(cls, valor):
        return str(valor) if valor is not None else None


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
    try:
        command = CreateVeiculoCommand(
            cliente_id=request.cliente_id,
            marca_id=request.marca_id,
            placa=request.placa,
            modelo=request.modelo,
            chassi=request.chassi,
            ano_fabricacao=request.ano_fabricacao,
        )

        return await use_case.execute(command)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


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

    if veiculo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=VEICULO_NAO_ENCONTRADO,
        )

    return veiculo


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
    try:
        command = UpdateVeiculoCommand(
            veiculo_id=veiculo_id,
            marca_id=request.marca_id,
            placa=request.placa,
            modelo=request.modelo,
            chassi=request.chassi,
            ano_fabricacao=request.ano_fabricacao,
        )

        veiculo = await use_case.execute(command)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if veiculo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=VEICULO_NAO_ENCONTRADO,
        )

    return veiculo


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
    try:
        excluido = await use_case.execute(
            DeleteVeiculoCommand(veiculo_id=veiculo_id)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not excluido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=VEICULO_NAO_ENCONTRADO,
        )
