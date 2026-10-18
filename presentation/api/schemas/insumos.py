"""Schemas (requests e responses) da API de insumos."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from domain.value_objects.dinheiro import Dinheiro


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
