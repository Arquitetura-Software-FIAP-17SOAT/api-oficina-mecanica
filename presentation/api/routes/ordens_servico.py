from fastapi import APIRouter, Depends, Query, status
from typing import Optional

from application.commands.criar_ordem_servico import (
    CriarOrdemServicoCommand,
    CriarOrdemServicoUseCase,
    InsumoSolicitado,
    ServicoSolicitado,
    VeiculoNaoEncontradoError,
)
from application.commands.adicionar_item_ordem_servico import (
    AdicionarItemOrdemServicoCommand,
    AdicionarItemOrdemServicoUseCase,
    ServicoNaoEncontradoError,
)
from application.commands.remover_item_ordem_servico import (
    RemoverItemOrdemServicoCommand,
    RemoverItemOrdemServicoUseCase,
)
from application.commands.adicionar_insumo_ordem_servico import (
    AdicionarInsumoOrdemServicoCommand,
    AdicionarInsumoOrdemServicoUseCase,
    InsumoNaoEncontradoError,
)
from application.commands.remover_insumo_ordem_servico import (
    RemoverInsumoOrdemServicoCommand,
    RemoverInsumoOrdemServicoUseCase,
)
from application.commands.iniciar_diagnostico_ordem_servico import (
    IniciarDiagnosticoOrdemServicoCommand,
    IniciarDiagnosticoOrdemServicoUseCase,
)
from application.commands.enviar_ordem_servico_para_aprovacao import (
    EnviarOrdemServicoParaAprovacaoCommand,
    EnviarOrdemServicoParaAprovacaoUseCase,
)
from application.commands.aprovar_orcamento_ordem_servico import (
    AprovarOrcamentoOrdemServicoCommand,
    AprovarOrcamentoOrdemServicoUseCase,
)
from application.commands.rejeitar_orcamento_ordem_servico import (
    RejeitarOrcamentoOrdemServicoCommand,
    RejeitarOrcamentoOrdemServicoUseCase,
)
from application.commands.finalizar_ordem_servico import (
    FinalizarOrdemServicoCommand,
    FinalizarOrdemServicoUseCase,
)
from application.commands.entregar_ordem_servico import (
    EntregarOrdemServicoCommand,
    EntregarOrdemServicoUseCase,
)
from application.commands.retornar_ordem_servico_para_diagnostico import (
    RetornarOrdemServicoParaDiagnosticoCommand,
    RetornarOrdemServicoParaDiagnosticoUseCase,
)
from application.commands.iniciar_execucao_servico import (
    IniciarExecucaoServicoCommand,
    IniciarExecucaoServicoUseCase,
    OrdemServicoNaoEncontradaError,
)
from application.commands.finalizar_execucao_servico import (
    FinalizarExecucaoServicoCommand,
    FinalizarExecucaoServicoUseCase,
)
from application.queries.get_ordem_servico_detalhada import (
    GetOrdemServicoDetalhadaUseCase,
    OrdemServicoDetalhada,
)
from application.queries.list_ordens_servico import (
    ListOrdensServicoQuery,
    ListOrdensServicoUseCase,
    OrdensServicoPaginadas,
)
from application.queries.list_tempo_medio_execucao import (
    ListTempoMedioExecucaoUseCase,
)
from presentation.api.error_handling import ordem_servico_ou_404, traduzir_erros
from presentation.api.mappers.ordens_servico import (
    para_detail_response,
    para_execucao_response,
    parse_data_iso,
    resposta_status,
)
from presentation.api.schemas.ordens_servico import (
    AdicionarInsumoRequest,
    AdicionarItemRequest,
    CriarOrdemServicoRequest,
    CriarOrdemServicoResponse,
    EntregarOSRequest,
    EnviarParaAprovacaoRequest,
    ExecucaoServicoResponse,
    FinalizarExecucaoRequest,
    FinalizarOSRequest,
    IniciarDiagnosticoRequest,
    IniciarExecucaoRequest,
    OrdemServicoDetailResponse,
    OrdemServicoResponse,
    OrdensServicoPaginadasResponse,
    RemoverInsumoRequest,
    RemoverItemRequest,
    RetornarDiagnosticoRequest,
    StatusChangeResponse,
    TempoMedioExecucaoResponse,
)
from presentation.dependencies.auth_dependencies import get_current_user
from presentation.dependencies.dependencies import (
    get_adicionar_item_ordem_servico_use_case,
    get_remover_item_ordem_servico_use_case,
    get_adicionar_insumo_ordem_servico_use_case,
    get_remover_insumo_ordem_servico_use_case,
    get_aprovar_orcamento_use_case,
    get_rejeitar_orcamento_use_case,
    get_criar_ordem_servico_use_case,
    get_entregar_ordem_servico_use_case,
    get_enviar_ordem_servico_para_aprovacao_use_case,
    get_finalizar_ordem_servico_use_case,
    get_iniciar_diagnostico_use_case,
    get_list_ordens_servico_use_case,
    get_ordem_servico_detalhada_use_case,
    get_retornar_ordem_servico_para_diagnostico_use_case,
    get_iniciar_execucao_servico_use_case,
    get_finalizar_execucao_servico_use_case,
    get_list_tempo_medio_execucao_use_case,
)

router = APIRouter(
    prefix="/ordens-servico",
    tags=["Ordens de Serviço"],
    dependencies=[Depends(get_current_user)],
)

# ==================== Endpoints ====================

@router.post(
    "",
    response_model=CriarOrdemServicoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar Ordem de Serviço",
    description="Cria uma nova ordem de serviço com status inicial 'Recebida'",
)
async def criar_ordem_servico(
    request: CriarOrdemServicoRequest,
    use_case: CriarOrdemServicoUseCase = Depends(get_criar_ordem_servico_use_case),
):
    """
    Cria uma nova ordem de serviço.

    A ordem de serviço é criada com status 'Recebida' e segue o fluxo:
    - Recebida → Em diagnóstico → Aguardando aprovação → Em execução → Finalizada → Entregue

    Validações aplicadas:
    - cliente_id e veiculo_id: obrigatórios; o veículo precisa pertencer ao cliente
    - servicos e insumos: opcionais; o estoque dos insumos é baixado na criação
    - descricao: mínimo 3 caracteres, máximo 1000
    - orcamento: opcional, deve ser positivo se informado
    """
    with traduzir_erros(
        "Erro ao criar ordem de serviço",
        nao_encontrado=(
            VeiculoNaoEncontradoError,
            ServicoNaoEncontradoError,
            InsumoNaoEncontradoError,
        ),
    ):
        ordem_servico = await use_case.execute(
            CriarOrdemServicoCommand(
                veiculo_id=request.veiculo_id,
                descricao=request.descricao,
                orcamento=request.orcamento,
                observacoes=request.observacoes,
                cliente_id=request.cliente_id,
                servicos=[
                    ServicoSolicitado(servico_id=s.servico_id, quantidade=s.quantidade)
                    for s in request.servicos
                ],
                insumos=[
                    InsumoSolicitado(insumo_id=i.insumo_id, quantidade=i.quantidade)
                    for i in request.insumos
                ],
            )
        )

        return CriarOrdemServicoResponse(
            id=ordem_servico.id,
            veiculo_id=ordem_servico.veiculo_id,
            descricao=str(ordem_servico.descricao),
            status=ordem_servico.status.value,
            quantidade_servicos=len(ordem_servico.itens),
            quantidade_insumos=len(ordem_servico.insumos_utilizados),
        )


@router.get(
    "",
    response_model=OrdensServicoPaginadasResponse,
    summary="Listar Ordens de Serviço",
    description=(
        "Lista as ordens de serviço com paginação, podendo ser filtradas por "
        "status, CPF/CNPJ do cliente ou placa do veículo. "
        "Ordenada por prioridade de status (Em execução, Aguardando aprovação, "
        "Em diagnóstico, Recebida) e, dentro do mesmo status, das mais antigas "
        "para as mais novas. OS Finalizadas e Entregues não aparecem na "
        "listagem (continuam consultáveis pelo detalhe). "
        "**Requer autenticação (Bearer token).**"
    ),
)
async def listar_ordens_servico(
    status_filtro: Optional[str] = Query(
        None,
        alias="status",
        description="Filtra pelo status exato da OS (ex.: 'Em diagnóstico').",
    ),
    cpf_cnpj: Optional[str] = Query(
        None, description="Filtra pelo CPF/CNPJ do cliente, com ou sem máscara."
    ),
    placa: Optional[str] = Query(
        None, description="Filtra pela placa do veículo, com ou sem máscara."
    ),
    page: int = Query(1, ge=1, description="Número da página (a partir de 1)."),
    page_size: int = Query(
        10, ge=1, le=100, description="Quantidade de itens por página (máx. 100)."
    ),
    use_case: ListOrdensServicoUseCase = Depends(get_list_ordens_servico_use_case),
):
    """Lista ordens de serviço de forma paginada, com filtros opcionais."""
    with traduzir_erros("Erro ao listar ordens de serviço"):
        resultado: OrdensServicoPaginadas = await use_case.execute(
            ListOrdensServicoQuery(
                status=status_filtro,
                cpf_cnpj=cpf_cnpj,
                placa=placa,
                page=page,
                page_size=page_size,
            )
        )

        return OrdensServicoPaginadasResponse(
            itens=[
                OrdemServicoResponse(
                    id=os.id,
                    veiculo_id=os.veiculo_id,
                    descricao=str(os.descricao),
                    status=os.status.value,
                    orcamento=os.orcamento,
                    status_orcamento=os.status_orcamento.value,
                    observacoes=os.observacoes,
                    quantidade_servicos=len(os.itens),
                )
                for os in resultado.itens
            ],
            total=resultado.total,
            page=resultado.page,
            page_size=resultado.page_size,
            total_paginas=resultado.total_paginas,
        )


@router.get(
    "/metricas/tempo-medio-execucao",
    response_model=list[TempoMedioExecucaoResponse],
    summary="Tempo Médio de Execução por Serviço",
    description=(
        "Retorna, para cada serviço do catálogo com execuções concluídas, o "
        "tempo médio em horas e a quantidade de execuções consideradas. "
        "**Requer autenticação (Bearer token).**"
    ),
)
async def listar_tempo_medio_execucao(
    use_case: ListTempoMedioExecucaoUseCase = Depends(
        get_list_tempo_medio_execucao_use_case
    ),
):
    """Consulta a métrica de monitoramento do tempo médio de execução dos serviços."""
    with traduzir_erros("Erro ao consultar tempo médio de execução"):
        metricas = await use_case.execute()

        return [
            TempoMedioExecucaoResponse(
                servico_id=metrica.servico_id,
                nome_servico=metrica.nome_servico,
                tempo_medio_horas=metrica.tempo_medio_horas,
                quantidade_execucoes=metrica.quantidade_execucoes,
            )
            for metrica in metricas
        ]


@router.get(
    "/{ordem_id}",
    response_model=OrdemServicoDetailResponse,
    summary="Obter Ordem de Serviço",
    description=(
        "Retorna os dados completos de uma ordem de serviço: cliente, "
        "veículo, serviços com suas peças/insumos, status e orçamento. "
        "**Requer autenticação (Bearer token).**"
    ),
)
async def obter_ordem_servico(
    ordem_id: int,
    use_case: GetOrdemServicoDetalhadaUseCase = Depends(
        get_ordem_servico_detalhada_use_case
    ),
):
    """
    Obtém os detalhes completos de uma ordem de serviço.

    Retorna:
    - Dados do cliente e do veículo atendidos
    - Status atual e orçamento
    - Serviços adicionados, cada um com as peças/insumos que consome
    - Valor total dos itens adicionados
    """
    with traduzir_erros("Erro ao obter ordem de serviço"):
        detalhe: OrdemServicoDetalhada | None = await use_case.execute(ordem_id)

        return para_detail_response(ordem_servico_ou_404(detalhe, ordem_id))


@router.post(
    "/{ordem_id}/iniciar-diagnostico",
    response_model=StatusChangeResponse,
    summary="Iniciar Diagnóstico",
    description="Move a OS para status 'Em diagnóstico'",
)
async def iniciar_diagnostico(
    ordem_id: int,
    request: IniciarDiagnosticoRequest,
    use_case: IniciarDiagnosticoOrdemServicoUseCase = Depends(
        get_iniciar_diagnostico_use_case
    ),
):
    """Inicia o diagnóstico de uma ordem de serviço"""
    with traduzir_erros("Erro ao iniciar diagnóstico"):
        ordem_servico = ordem_servico_ou_404(
            await use_case.execute(
                IniciarDiagnosticoOrdemServicoCommand(
                    ordem_servico_id=ordem_id,
                    observacoes=request.observacoes,
                )
            ),
            ordem_id,
        )

        return resposta_status(ordem_servico, "Diagnóstico iniciado com sucesso")


@router.post(
    "/{ordem_id}/enviar-aprovacao",
    response_model=StatusChangeResponse,
    summary="Enviar para Aprovação",
    description="Move a OS para status 'Aguardando aprovação' com orçamento definido",
)
async def enviar_para_aprovacao(
    ordem_id: int,
    request: EnviarParaAprovacaoRequest,
    use_case: EnviarOrdemServicoParaAprovacaoUseCase = Depends(
        get_enviar_ordem_servico_para_aprovacao_use_case
    ),
):
    """Envia ordem de serviço para aprovação do cliente"""
    with traduzir_erros("Erro ao enviar para aprovação"):
        ordem_servico = ordem_servico_ou_404(
            await use_case.execute(
                EnviarOrdemServicoParaAprovacaoCommand(
                    ordem_servico_id=ordem_id,
                    orcamento=request.orcamento,
                    observacoes=request.observacoes,
                )
            ),
            ordem_id,
        )

        return resposta_status(
            ordem_servico,
            f"Ordem enviada para aprovação. Orçamento: R$ {ordem_servico.orcamento:.2f}",
        )


@router.post(
    "/{ordem_id}/adicionar-item",
    response_model=StatusChangeResponse,
    summary="Adicionar Serviço",
    description="Adiciona um serviço (item) à ordem de serviço",
)
async def adicionar_item(
    ordem_id: int,
    request: AdicionarItemRequest,
    use_case: AdicionarItemOrdemServicoUseCase = Depends(
        get_adicionar_item_ordem_servico_use_case
    ),
):
    """Adiciona um serviço à ordem de serviço"""
    with traduzir_erros(
        "Erro ao adicionar serviço", nao_encontrado=(ServicoNaoEncontradoError,)
    ):
        ordem_servico = ordem_servico_ou_404(
            await use_case.execute(
                AdicionarItemOrdemServicoCommand(
                    ordem_servico_id=ordem_id,
                    servico_id=request.servico_id,
                    quantidade=request.quantidade,
                )
            ),
            ordem_id,
        )

        return resposta_status(
            ordem_servico,
            f"Serviço adicionado. Total de serviços: {len(ordem_servico.itens)}",
        )


@router.post(
    "/{ordem_id}/remover-item",
    response_model=StatusChangeResponse,
    summary="Remover Serviço",
    description="Remove um serviço (item) da ordem de serviço",
)
async def remover_item(
    ordem_id: int,
    request: RemoverItemRequest,
    use_case: RemoverItemOrdemServicoUseCase = Depends(
        get_remover_item_ordem_servico_use_case
    ),
):
    """Remove um serviço da ordem de serviço"""
    with traduzir_erros("Erro ao remover serviço"):
        ordem_servico = ordem_servico_ou_404(
            await use_case.execute(
                RemoverItemOrdemServicoCommand(
                    ordem_servico_id=ordem_id,
                    servico_id=request.servico_id,
                )
            ),
            ordem_id,
        )

        return resposta_status(
            ordem_servico,
            f"Serviço removido. Total de serviços: {len(ordem_servico.itens)}",
        )


@router.post(
    "/{ordem_id}/adicionar-insumo",
    response_model=StatusChangeResponse,
    summary="Adicionar Insumo",
    description=(
        "Registra uma peça/insumo avulso consumido na ordem de serviço, fora "
        "da composição fixa de um serviço, e dá baixa no estoque."
    ),
)
async def adicionar_insumo(
    ordem_id: int,
    request: AdicionarInsumoRequest,
    use_case: AdicionarInsumoOrdemServicoUseCase = Depends(
        get_adicionar_insumo_ordem_servico_use_case
    ),
):
    """Registra o consumo de um insumo avulso na ordem de serviço"""
    with traduzir_erros(
        "Erro ao adicionar insumo", nao_encontrado=(InsumoNaoEncontradoError,)
    ):
        ordem_servico = ordem_servico_ou_404(
            await use_case.execute(
                AdicionarInsumoOrdemServicoCommand(
                    ordem_servico_id=ordem_id,
                    insumo_id=request.insumo_id,
                    quantidade=request.quantidade,
                )
            ),
            ordem_id,
        )

        return resposta_status(
            ordem_servico,
            f"Insumo adicionado. Total de insumos: {len(ordem_servico.insumos_utilizados)}",
        )


@router.post(
    "/{ordem_id}/remover-insumo",
    response_model=StatusChangeResponse,
    summary="Remover Insumo",
    description=(
        "Remove um insumo avulso da ordem de serviço e estorna a "
        "quantidade ao estoque."
    ),
)
async def remover_insumo(
    ordem_id: int,
    request: RemoverInsumoRequest,
    use_case: RemoverInsumoOrdemServicoUseCase = Depends(
        get_remover_insumo_ordem_servico_use_case
    ),
):
    """Remove um insumo avulso da ordem de serviço"""
    with traduzir_erros("Erro ao remover insumo"):
        ordem_servico = ordem_servico_ou_404(
            await use_case.execute(
                RemoverInsumoOrdemServicoCommand(
                    ordem_servico_id=ordem_id,
                    insumo_id=request.insumo_id,
                )
            ),
            ordem_id,
        )

        return resposta_status(
            ordem_servico,
            f"Insumo removido. Total de insumos: {len(ordem_servico.insumos_utilizados)}",
        )


@router.post(
    "/{ordem_id}/aprovar-executar",
    response_model=StatusChangeResponse,
    summary="Aprovar e Iniciar Execução",
    description="Aprova a OS e move para status 'Em execução'",
)
async def aprovar_e_executar(
    ordem_id: int,
    use_case: AprovarOrcamentoOrdemServicoUseCase = Depends(
        get_aprovar_orcamento_use_case
    ),
):
    """Aprova a ordem de serviço e inicia a execução.

    Este é o endpoint acionado pelo gatilho externo de aprovação do
    cliente (ex.: confirmação via aplicativo). Toda a regra de transição
    de status e a persistência ficam encapsuladas em
    ``AprovarOrcamentoOrdemServicoUseCase``.
    """
    with traduzir_erros("Erro ao aprovar execução"):
        ordem_servico = ordem_servico_ou_404(
            await use_case.execute(
                AprovarOrcamentoOrdemServicoCommand(ordem_servico_id=ordem_id)
            ),
            ordem_id,
        )

        return resposta_status(ordem_servico, "Ordem aprovada e execução iniciada")


@router.post(
    "/{ordem_id}/rejeitar-orcamento",
    response_model=StatusChangeResponse,
    summary="Rejeitar Orçamento",
    description="Rejeita o orçamento e move a OS para status 'Finalizada'",
)
async def rejeitar_orcamento(
    ordem_id: int,
    use_case: RejeitarOrcamentoOrdemServicoUseCase = Depends(
        get_rejeitar_orcamento_use_case
    ),
):
    """Rejeita o orçamento e encerra a ordem de serviço."""
    with traduzir_erros("Erro ao rejeitar orçamento"):
        ordem_servico = ordem_servico_ou_404(
            await use_case.execute(
                RejeitarOrcamentoOrdemServicoCommand(ordem_servico_id=ordem_id)
            ),
            ordem_id,
        )

        return resposta_status(
            ordem_servico, "Orçamento rejeitado e ordem de serviço finalizada"
        )


@router.post(
    "/{ordem_id}/finalizar",
    response_model=StatusChangeResponse,
    summary="Finalizar Ordem",
    description="Move a OS para status 'Finalizada' (serviços concluídos)",
)
async def finalizar(
    ordem_id: int,
    request: FinalizarOSRequest,
    use_case: FinalizarOrdemServicoUseCase = Depends(
        get_finalizar_ordem_servico_use_case
    ),
):
    """Finaliza a ordem de serviço"""
    with traduzir_erros("Erro ao finalizar ordem"):
        ordem_servico = ordem_servico_ou_404(
            await use_case.execute(
                FinalizarOrdemServicoCommand(
                    ordem_servico_id=ordem_id,
                    observacoes=request.observacoes,
                )
            ),
            ordem_id,
        )

        return resposta_status(ordem_servico, "Ordem finalizada com sucesso")


@router.post(
    "/{ordem_id}/entregar",
    response_model=StatusChangeResponse,
    summary="Entregar Ordem",
    description="Move a OS para status 'Entregue' (estado final)",
)
async def entregar(
    ordem_id: int,
    request: EntregarOSRequest,
    use_case: EntregarOrdemServicoUseCase = Depends(
        get_entregar_ordem_servico_use_case
    ),
):
    """Entrega a ordem de serviço ao cliente"""
    with traduzir_erros("Erro ao entregar ordem"):
        ordem_servico = ordem_servico_ou_404(
            await use_case.execute(
                EntregarOrdemServicoCommand(
                    ordem_servico_id=ordem_id,
                    observacoes=request.observacoes,
                )
            ),
            ordem_id,
        )

        return resposta_status(ordem_servico, "Ordem entregue com sucesso")


@router.post(
    "/{ordem_id}/retornar-diagnostico",
    response_model=StatusChangeResponse,
    summary="Retornar para Diagnóstico",
    description="Retorna a OS para 'Em diagnóstico' (cliente não aprova)",
)
async def retornar_diagnostico(
    ordem_id: int,
    request: RetornarDiagnosticoRequest,
    use_case: RetornarOrdemServicoParaDiagnosticoUseCase = Depends(
        get_retornar_ordem_servico_para_diagnostico_use_case
    ),
):
    """Retorna a ordem de serviço para diagnóstico"""
    with traduzir_erros("Erro ao retornar para diagnóstico"):
        ordem_servico = ordem_servico_ou_404(
            await use_case.execute(
                RetornarOrdemServicoParaDiagnosticoCommand(
                    ordem_servico_id=ordem_id,
                    motivo=request.motivo,
                )
            ),
            ordem_id,
        )

        return resposta_status(ordem_servico, "Ordem retornada para diagnóstico")


@router.post(
    "/{ordem_id}/servicos/{servico_id}/iniciar",
    response_model=ExecucaoServicoResponse,
    summary="Iniciar Execução de Serviço",
    description="Registra o início da execução de um serviço específico em uma ordem de serviço",
)
async def iniciar_execucao_servico(
    ordem_id: int,
    servico_id: int,
    request: IniciarExecucaoRequest,
    use_case: IniciarExecucaoServicoUseCase = Depends(
        get_iniciar_execucao_servico_use_case
    ),
):
    """
    Registra quando um serviço inicia sua execução.

    Validações:
    - Ordem de serviço deve existir
    - Serviço deve estar adicionado à ordem
    - Serviço não pode já ter começado
    - data_inicio não pode ser no futuro
    """
    with traduzir_erros(
        "Erro ao iniciar execução do serviço",
        nao_encontrado=(OrdemServicoNaoEncontradaError,),
    ):
        resultado = await use_case.execute(
            IniciarExecucaoServicoCommand(
                ordem_servico_id=ordem_id,
                servico_id=servico_id,
                data_inicio=parse_data_iso(request.data_inicio),
            )
        )

        return para_execucao_response(resultado)


@router.post(
    "/{ordem_id}/servicos/{servico_id}/finalizar",
    response_model=ExecucaoServicoResponse,
    summary="Finalizar Execução de Serviço",
    description="Registra o fim da execução de um serviço específico e calcula o tempo total",
)
async def finalizar_execucao_servico(
    ordem_id: int,
    servico_id: int,
    request: FinalizarExecucaoRequest,
    use_case: FinalizarExecucaoServicoUseCase = Depends(
        get_finalizar_execucao_servico_use_case
    ),
):
    """
    Registra quando um serviço finaliza sua execução.

    Calcula e retorna o tempo total de execução em horas.

    Validações:
    - Ordem de serviço deve existir
    - Serviço deve estar adicionado à ordem
    - Serviço deve ter um data_inicio registrado
    - data_fim não pode ser anterior a data_inicio
    - data_fim não pode ser no futuro
    """
    with traduzir_erros(
        "Erro ao finalizar execução do serviço",
        nao_encontrado=(OrdemServicoNaoEncontradaError,),
    ):
        resultado = await use_case.execute(
            FinalizarExecucaoServicoCommand(
                ordem_servico_id=ordem_id,
                servico_id=servico_id,
                data_fim=parse_data_iso(request.data_fim),
            )
        )

        return para_execucao_response(resultado)
