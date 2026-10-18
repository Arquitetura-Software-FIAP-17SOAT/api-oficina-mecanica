"""Entrada de notificações de sistemas externos.

Router separado de ``ordens_servico.py`` pelo mesmo motivo de
``consulta_publica.py``: lá todas as rotas exigem o JWT de um funcionário, e
um sistema externo se autentica por chave de API (``X-API-Key``).
"""

from typing import Literal, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from application.commands.aprovar_orcamento_ordem_servico import (
    AprovarOrcamentoOrdemServicoCommand,
    AprovarOrcamentoOrdemServicoUseCase,
)
from application.commands.entregar_ordem_servico import (
    EntregarOrdemServicoCommand,
    EntregarOrdemServicoUseCase,
)
from application.commands.enviar_ordem_servico_para_aprovacao import (
    EnviarOrdemServicoParaAprovacaoCommand,
    EnviarOrdemServicoParaAprovacaoUseCase,
)
from application.commands.finalizar_ordem_servico import (
    FinalizarOrdemServicoCommand,
    FinalizarOrdemServicoUseCase,
)
from application.commands.iniciar_diagnostico_ordem_servico import (
    IniciarDiagnosticoOrdemServicoCommand,
    IniciarDiagnosticoOrdemServicoUseCase,
)
from application.commands.rejeitar_orcamento_ordem_servico import (
    RejeitarOrcamentoOrdemServicoCommand,
    RejeitarOrcamentoOrdemServicoUseCase,
)
from application.commands.retornar_ordem_servico_para_diagnostico import (
    RetornarOrdemServicoParaDiagnosticoCommand,
    RetornarOrdemServicoParaDiagnosticoUseCase,
)
from presentation.api.error_handling import ordem_servico_ou_404, traduzir_erros
from presentation.dependencies.dependencies import (
    get_aprovar_orcamento_use_case,
    get_entregar_ordem_servico_use_case,
    get_enviar_ordem_servico_para_aprovacao_use_case,
    get_finalizar_ordem_servico_use_case,
    get_iniciar_diagnostico_use_case,
    get_rejeitar_orcamento_use_case,
    get_retornar_ordem_servico_para_diagnostico_use_case,
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


@router.post(
    "/ordens-servico/{ordem_id}/status",
    response_model=AtualizacaoStatusResponse,
    summary="Atualizar o status da OS por uma ferramenta externa",
    description=(
        "Recebe de uma ferramenta externa (por exemplo, um e-mail já "
        "interpretado) a ação que muda o status da OS. As mesmas regras de "
        "transição dos endpoints administrativos valem aqui; ação inválida "
        "para o status atual retorna 400. A decisão sobre o orçamento tem "
        "endpoint próprio (`/orcamento`). "
        "**Autenticação por chave de API (header `X-API-Key`).**"
    ),
)
async def atualizar_status_externo(
    ordem_id: int,
    request: AtualizacaoStatusRequest,
    iniciar_diagnostico: IniciarDiagnosticoOrdemServicoUseCase = Depends(
        get_iniciar_diagnostico_use_case
    ),
    enviar_para_aprovacao: EnviarOrdemServicoParaAprovacaoUseCase = Depends(
        get_enviar_ordem_servico_para_aprovacao_use_case
    ),
    retornar_para_diagnostico: RetornarOrdemServicoParaDiagnosticoUseCase = Depends(
        get_retornar_ordem_servico_para_diagnostico_use_case
    ),
    finalizar: FinalizarOrdemServicoUseCase = Depends(
        get_finalizar_ordem_servico_use_case
    ),
    entregar: EntregarOrdemServicoUseCase = Depends(
        get_entregar_ordem_servico_use_case
    ),
):
    texto = request.observacoes

    execucoes = {
        "iniciar_diagnostico": lambda: iniciar_diagnostico.execute(
            IniciarDiagnosticoOrdemServicoCommand(
                ordem_servico_id=ordem_id, observacoes=texto
            )
        ),
        "enviar_para_aprovacao": lambda: enviar_para_aprovacao.execute(
            EnviarOrdemServicoParaAprovacaoCommand(
                ordem_servico_id=ordem_id, orcamento=None, observacoes=texto
            )
        ),
        "retornar_para_diagnostico": lambda: retornar_para_diagnostico.execute(
            RetornarOrdemServicoParaDiagnosticoCommand(
                ordem_servico_id=ordem_id, motivo=texto
            )
        ),
        "finalizar": lambda: finalizar.execute(
            FinalizarOrdemServicoCommand(ordem_servico_id=ordem_id, observacoes=texto)
        ),
        "entregar": lambda: entregar.execute(
            EntregarOrdemServicoCommand(ordem_servico_id=ordem_id, observacoes=texto)
        ),
    }

    with traduzir_erros("Erro ao atualizar o status da ordem de serviço"):
        ordem_servico = ordem_servico_ou_404(
            await execucoes[request.acao](), ordem_id
        )

        return AtualizacaoStatusResponse(
            ordem_servico_id=ordem_servico.id,
            status=ordem_servico.status.value,
            message=f"Status atualizado para '{ordem_servico.status.value}'",
        )
