"""Schemas (requests e responses) da API de veículos."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from domain.value_objects.data_hora import DataHora


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
