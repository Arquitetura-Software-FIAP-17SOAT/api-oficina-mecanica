"""Schemas (requests e responses) das integrações externas."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class DecisaoOrcamentoRequest(BaseModel):
    """Decisão do cliente sobre o orçamento, informada por um sistema externo."""

    decisao: Literal["aprovado", "recusado"] = Field(
        description="Se o cliente aprovou ou recusou o orçamento.",
        examples=["aprovado"],
    )


class DecisaoOrcamentoResponse(BaseModel):
    ordem_servico_id: int
    status: str
    status_orcamento: str
    message: str


AcaoStatus = Literal[
    "iniciar_diagnostico",
    "enviar_para_aprovacao",
    "retornar_para_diagnostico",
    "finalizar",
    "entregar",
]


class AtualizacaoStatusRequest(BaseModel):
    """Pedido de mudança de status vindo de uma ferramenta externa (ex.: e-mail)."""

    acao: AcaoStatus = Field(
        description="Ação que muda o status da OS.",
        examples=["iniciar_diagnostico"],
    )
    observacoes: Optional[str] = Field(
        None,
        description=(
            "Texto livre do e-mail. Vira observação da OS (ou o motivo, em "
            "`retornar_para_diagnostico`)."
        ),
    )


class AtualizacaoStatusResponse(BaseModel):
    ordem_servico_id: int
    status: str
    message: str
