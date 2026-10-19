"""Rota de acompanhamento da OS pelo próprio cliente, sem login administrativo.

Vive num módulo e num router separados de ``ordens_servico.py`` de propósito.
Aquele router aplica ``Depends(get_current_user)`` no nível do ``APIRouter``, e
o FastAPI não permite que um endpoint específico abra mão de uma dependência de
router — então uma rota pública ali seria impossível. A separação também deixa
a fronteira de segurança explícita: tudo neste arquivo é acessível sem token, e
por isso responde com menos dados que a rota administrativa equivalente.
"""


from fastapi import APIRouter, Depends, HTTPException, status

from application.queries.consultar_ordem_servico_publica import (
    ConsultarOrdemServicoPublicaQuery,
    ConsultarOrdemServicoPublicaUseCase,
)
from presentation.api.mappers.consulta_publica import para_acompanhamento_response
from presentation.api.schemas.consulta_publica import (
    AcompanhamentoOrdemServicoResponse,
    ConsultarOrdemServicoRequest,
)
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

    return para_acompanhamento_response(detalhe)
