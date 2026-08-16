"""Rota de acompanhamento da OS pelo próprio cliente, sem login administrativo.

Vive num módulo e num router separados de ``ordens_servico.py`` de propósito.
Aquele router aplica ``Depends(get_current_user)`` no nível do ``APIRouter``, e
o FastAPI não permite que um endpoint específico abra mão de uma dependência de
router — então uma rota pública ali seria impossível. A separação também deixa
a fronteira de segurança explícita: tudo neste arquivo é acessível sem token, e
por isso responde com menos dados que a rota administrativa equivalente.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from application.queries.consultar_ordem_servico_publica import (
    ConsultarOrdemServicoPublicaQuery,
    ConsultarOrdemServicoPublicaUseCase,
)
from application.queries.get_ordem_servico_detalhada import OrdemServicoDetalhada
from domain.value_objects.status_ordem_servico import StatusOrdemServico
from presentation.dependencies.dependencies import (
    get_consultar_ordem_servico_publica_use_case,
)

router = APIRouter(
    prefix="/consulta",
    tags=["Consulta do Cliente"],
)

ORDEM_NAO_ENCONTRADA = (
    "Ordem de serviço não encontrada para o número e documento informados."
)


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


@router.post(
    "/ordens-servico",
    response_model=AcompanhamentoOrdemServicoResponse,
    status_code=status.HTTP_200_OK,
    summary="Acompanhar ordem de serviço (cliente)",
    description=(
        "Permite que o cliente acompanhe o andamento da própria ordem de "
        "serviço **sem autenticação administrativa**, informando o número da "
        "OS e o CPF/CNPJ cadastrado nela. "
        "Devolve 404 tanto quando a OS não existe quanto quando o documento "
        "não confere, para não revelar quais ordens existem."
    ),
)
async def consultar_ordem_servico(
    request: ConsultarOrdemServicoRequest,
    use_case: ConsultarOrdemServicoPublicaUseCase = Depends(
        get_consultar_ordem_servico_publica_use_case
    ),
):
    """Consulta pública de acompanhamento da OS.

    É um POST, e não um GET, porque o CPF/CNPJ é dado pessoal: em um GET ele
    iria na query string e acabaria gravado em log de acesso, histórico do
    navegador e cabeçalho ``Referer``. No corpo da requisição, não.
    """
    detalhe = await use_case.execute(
        ConsultarOrdemServicoPublicaQuery(
            numero_os=request.numero_os,
            cpf_cnpj=request.cpf_cnpj,
        )
    )

    if detalhe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ORDEM_NAO_ENCONTRADA,
        )

    return _para_acompanhamento_response(detalhe)


def _para_acompanhamento_response(
    detalhe: OrdemServicoDetalhada,
) -> AcompanhamentoOrdemServicoResponse:
    ordem_servico = detalhe.ordem_servico

    return AcompanhamentoOrdemServicoResponse(
        numero_os=ordem_servico.id,
        status=ordem_servico.status.value,
        status_descricao=StatusOrdemServico.descrever_status(ordem_servico.status),
        descricao=str(ordem_servico.descricao),
        veiculo=(
            VeiculoAcompanhamentoResponse(
                placa=str(detalhe.veiculo.placa),
                modelo=detalhe.veiculo.modelo,
            )
            if detalhe.veiculo
            else None
        ),
        servicos=[
            ServicoAcompanhamentoResponse(
                nome=item.servico.nome if item.servico else None,
                quantidade=item.quantidade,
                valor_total=item.valor_total,
            )
            for item in detalhe.itens
        ],
        orcamento=ordem_servico.orcamento,
        valor_total_servicos=detalhe.valor_total_itens,
        aguardando_sua_aprovacao=(
            ordem_servico.status == StatusOrdemServico.AGUARDANDO_APROVACAO
        ),
        atualizado_em=ordem_servico.data_atualizacao,
    )
