"""Schemas (requests e responses) da consulta do cliente."""

from datetime import datetime
from typing import Optional

from fastapi import status
from pydantic import BaseModel, ConfigDict, Field


class ConsultarOrdemServicoRequest(BaseModel):
    """Dados que só o dono da OS reúne: o número dela e o próprio documento."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"numero_os": 1, "cpf_cnpj": "529.982.247-25"}
        }
    )

    numero_os: int = Field(
        description="Número da ordem de serviço, informado na abertura.",
        examples=[1],
    )
    cpf_cnpj: str = Field(
        description=(
            "CPF ou CNPJ cadastrado na ordem de serviço. "
            "Aceita com ou sem máscara."
        ),
        examples=["529.982.247-25"],
    )


class ServicoAcompanhamentoResponse(BaseModel):
    """Um serviço da OS, na visão do cliente."""

    nome: Optional[str] = None
    quantidade: int
    valor_total: float


class VeiculoAcompanhamentoResponse(BaseModel):
    """Só o suficiente para o cliente reconhecer o próprio veículo."""

    placa: str
    modelo: str


class AcompanhamentoOrdemServicoResponse(BaseModel):
    """Andamento da OS. Enxuta de propósito — é uma resposta pública.

    Não expõe identificadores internos (cliente, veículo, marca, usuário),
    e-mail do cliente nem observações — este último é texto livre preenchido
    por funcionários, que podem não contar com ele sendo visível ao cliente.
    """

    numero_os: int
    status: str
    status_descricao: str
    descricao: str
    veiculo: Optional[VeiculoAcompanhamentoResponse]
    servicos: list[ServicoAcompanhamentoResponse]
    orcamento: Optional[float]
    valor_total_servicos: float
    aguardando_sua_aprovacao: bool
    atualizado_em: datetime
