"""Conversores entre os resultados da aplicação e os schemas da API de OS."""

from datetime import datetime
from typing import Optional

from application.queries.get_ordem_servico_detalhada import (
    InsumoUtilizadoDetalhado,
    ItemServicoDetalhado,
    OrdemServicoDetalhada,
)
from presentation.api.schemas.ordens_servico import (
    ClienteResumoResponse,
    ExecucaoServicoResponse,
    InsumoResumoResponse,
    InsumoUtilizadoResponse,
    OrdemServicoDetailResponse,
    ServicoItemResponse,
    StatusChangeResponse,
    VeiculoResumoResponse,
)


def resposta_status(ordem_servico, message: str) -> StatusChangeResponse:
    return StatusChangeResponse(
        id=ordem_servico.id,
        status=ordem_servico.status.value,
        message=message,
    )


def parse_data_iso(valor: Optional[str]) -> Optional[datetime]:
    if not valor:
        return None
    return datetime.fromisoformat(valor.replace("Z", "+00:00"))


def isoformat_ou_none(valor: Optional[datetime]) -> Optional[str]:
    return valor.isoformat() if valor else None


def para_execucao_response(resultado: dict) -> ExecucaoServicoResponse:
    return ExecucaoServicoResponse(
        ordem_servico_id=resultado["ordem_servico_id"],
        servico_id=resultado["servico_id"],
        data_inicio=isoformat_ou_none(resultado["data_inicio"]),
        data_fim=isoformat_ou_none(resultado["data_fim"]),
        tempo_execucao_horas=resultado.get("tempo_execucao_horas"),
        mensagem=resultado["mensagem"],
    )


def para_detail_response(
    detalhe: OrdemServicoDetalhada,
) -> OrdemServicoDetailResponse:
    ordem_servico = detalhe.ordem_servico

    return OrdemServicoDetailResponse(
        id=ordem_servico.id,
        veiculo_id=ordem_servico.veiculo_id,
        descricao=str(ordem_servico.descricao),
        status=ordem_servico.status.value,
        orcamento=ordem_servico.orcamento,
        status_orcamento=ordem_servico.status_orcamento.value,
        observacoes=ordem_servico.observacoes,
        cliente=(
            ClienteResumoResponse(
                id=detalhe.cliente.id,
                nome=detalhe.cliente.nome,
                cpf_cnpj=(
                    str(detalhe.cliente.cpf_cnpj)
                    if detalhe.cliente.cpf_cnpj
                    else None
                ),
                email=str(detalhe.cliente.email) if detalhe.cliente.email else None,
            )
            if detalhe.cliente
            else None
        ),
        veiculo=(
            VeiculoResumoResponse(
                id=detalhe.veiculo.id,
                placa=str(detalhe.veiculo.placa),
                modelo=detalhe.veiculo.modelo,
                marca_id=detalhe.veiculo.marca_id,
                ano_fabricacao=detalhe.veiculo.ano_fabricacao,
            )
            if detalhe.veiculo
            else None
        ),
        itens=[para_item_response(item) for item in detalhe.itens],
        insumos_utilizados=[
            para_insumo_utilizado_response(item)
            for item in detalhe.insumos_utilizados
        ],
        valor_total_itens=detalhe.valor_total_itens,
    )


def para_item_response(item: ItemServicoDetalhado) -> ServicoItemResponse:
    return ServicoItemResponse(
        servico_id=item.servico_id,
        nome=item.servico.nome if item.servico else None,
        quantidade=item.quantidade,
        valor_unitario=item.valor_unitario,
        valor_total=item.valor_total,
        insumos=[
            InsumoResumoResponse(id=insumo.id, nome=insumo.nome, estoque=insumo.estoque)
            for insumo in item.insumos
        ],
    )


def para_insumo_utilizado_response(
    item: InsumoUtilizadoDetalhado,
) -> InsumoUtilizadoResponse:
    return InsumoUtilizadoResponse(
        insumo_id=item.insumo_id,
        nome=item.insumo.nome if item.insumo else None,
        quantidade=item.quantidade,
        valor_unitario=item.valor_unitario,
        valor_total=item.valor_total,
    )
