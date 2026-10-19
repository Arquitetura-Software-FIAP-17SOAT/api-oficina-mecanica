"""Schemas (requests e responses) da API de serviços."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from domain.value_objects.dinheiro import Dinheiro


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
