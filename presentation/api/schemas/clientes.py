"""Schemas (requests e responses) da API de clientes."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
