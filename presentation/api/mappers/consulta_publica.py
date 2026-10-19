"""Conversores do resultado da aplicação para os schemas de consulta_publica."""

from application.queries.get_ordem_servico_detalhada import OrdemServicoDetalhada
from domain.value_objects.status_ordem_servico import StatusOrdemServico
from presentation.api.schemas.consulta_publica import (
    AcompanhamentoOrdemServicoResponse,
    ServicoAcompanhamentoResponse,
    VeiculoAcompanhamentoResponse,
)


def para_acompanhamento_response(
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
