"""Entrada de notificações de sistemas externos.

Router separado de ``ordens_servico.py`` pelo mesmo motivo de
``consulta_publica.py``: lá todas as rotas exigem o JWT de um funcionário, e
um sistema externo se autentica por chave de API (``X-API-Key``).
"""

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from application.commands.aprovar_orcamento_ordem_servico import (
    AprovarOrcamentoOrdemServicoCommand,
    AprovarOrcamentoOrdemServicoUseCase,
)
from application.commands.rejeitar_orcamento_ordem_servico import (
    RejeitarOrcamentoOrdemServicoCommand,
    RejeitarOrcamentoOrdemServicoUseCase,
)
from presentation.api.error_handling import ordem_servico_ou_404, traduzir_erros
from presentation.dependencies.dependencies import (
    get_aprovar_orcamento_use_case,
    get_rejeitar_orcamento_use_case,
)
from presentation.dependencies.integracao_dependencies import validar_chave_integracao

router = APIRouter(
    prefix="/integracoes",
    tags=["Integrações Externas"],
    dependencies=[Depends(validar_chave_integracao)],
)


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


@router.post(
    "/ordens-servico/{ordem_id}/orcamento",
    response_model=DecisaoOrcamentoResponse,
    summary="Receber aprovação ou recusa do orçamento",
    description=(
        "Notificação de um sistema externo com a decisão do cliente sobre o "
        "orçamento. `aprovado` move a OS para 'Em execução'; `recusado` a "
        "move para 'Finalizada'. Só vale para OS em 'Aguardando aprovação'. "
        "**Autenticação por chave de API (header `X-API-Key`).**"
    ),
)
async def receber_decisao_orcamento(
    ordem_id: int,
    request: DecisaoOrcamentoRequest,
    aprovar: AprovarOrcamentoOrdemServicoUseCase = Depends(
        get_aprovar_orcamento_use_case
    ),
    rejeitar: RejeitarOrcamentoOrdemServicoUseCase = Depends(
        get_rejeitar_orcamento_use_case
    ),
):
    with traduzir_erros("Erro ao registrar a decisão do orçamento"):
        if request.decisao == "aprovado":
            resultado = await aprovar.execute(
                AprovarOrcamentoOrdemServicoCommand(ordem_servico_id=ordem_id)
            )
            mensagem = "Orçamento aprovado e execução iniciada"
        else:
            resultado = await rejeitar.execute(
                RejeitarOrcamentoOrdemServicoCommand(ordem_servico_id=ordem_id)
            )
            mensagem = "Orçamento recusado e ordem de serviço finalizada"

        ordem_servico = ordem_servico_ou_404(resultado, ordem_id)

        return DecisaoOrcamentoResponse(
            ordem_servico_id=ordem_servico.id,
            status=ordem_servico.status.value,
            status_orcamento=ordem_servico.status_orcamento.value,
            message=mensagem,
        )
