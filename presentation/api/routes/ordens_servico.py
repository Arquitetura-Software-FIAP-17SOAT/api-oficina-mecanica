from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

from infrastructure.database.database import get_db
from infrastructure.database.models import ServicoModel

from application.commands.criar_ordem_servico import (
    CriarOrdemServicoCommand,
    CriarOrdemServicoUseCase,
    VeiculoNaoEncontradoError,
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
from application.queries.get_ordem_servico_detalhada import (
    GetOrdemServicoDetalhadaUseCase,
    ItemServicoDetalhado,
    OrdemServicoDetalhada,
)
from application.queries.list_ordens_servico import (
    ListOrdensServicoQuery,
    ListOrdensServicoUseCase,
    OrdensServicoPaginadas,
)
from presentation.dependencies.auth_dependencies import get_current_user
from presentation.dependencies.dependencies import (
    get_aprovar_orcamento_use_case,
    get_criar_ordem_servico_use_case,
    get_entregar_ordem_servico_use_case,
    get_enviar_ordem_servico_para_aprovacao_use_case,
    get_finalizar_ordem_servico_use_case,
    get_iniciar_diagnostico_use_case,
    get_list_ordens_servico_use_case,
    get_ordem_servico_detalhada_use_case,
    get_retornar_ordem_servico_para_diagnostico_use_case,
)

router = APIRouter(
    prefix="/ordens-servico",
    tags=["Ordens de Serviço"],
    dependencies=[Depends(get_current_user)],
)


# ==================== Requests ====================

class CriarOrdemServicoRequest(BaseModel):
    """Request para criar uma nova ordem de serviço"""
    veiculo_id: str = Field(..., description="ID do veículo")
    descricao: str = Field(..., description="Descrição da ordem de serviço")
    orcamento: Optional[float] = Field(None, description="Orçamento estimado")
    observacoes: Optional[str] = Field(None, description="Observações adicionais")


class IniciarDiagnosticoRequest(BaseModel):
    """Request para iniciar diagnóstico"""
    observacoes: Optional[str] = Field(None, description="Observações do diagnóstico")


class EnviarParaAprovacaoRequest(BaseModel):
    """Request para enviar para aprovação"""
    orcamento: Optional[float] = Field(
        None,
        description=(
            "Orçamento a ser aprovado pelo cliente. Se omitido, é gerado "
            "automaticamente a partir dos serviços adicionados à OS. "
            "Informe um valor para aplicar desconto ou acréscimo sobre o total."
        ),
        examples=[350.00],
    )
    observacoes: Optional[str] = Field(None, description="Observações")


class AprovarRequest(BaseModel):
    """Request para aprovar e iniciar execução"""
    pass


class AdicionarItemRequest(BaseModel):
    """Request para adicionar serviço à ordem"""
    servico_id: str = Field(..., description="ID do serviço")
    quantidade: int = Field(1, description="Quantidade")


class RemoverItemRequest(BaseModel):
    """Request para remover serviço da ordem"""
    servico_id: str = Field(..., description="ID do serviço a remover")


class FinalizarOSRequest(BaseModel):
    """Request para finalizar OS"""
    observacoes: Optional[str] = Field(None, description="Observações finais")


class EntregarOSRequest(BaseModel):
    """Request para entregar OS"""
    observacoes: Optional[str] = Field(None, description="Observações na entrega")


class RetornarDiagnosticoRequest(BaseModel):
    """Request para retornar para diagnóstico"""
    motivo: Optional[str] = Field(None, description="Motivo da devolução")


# ==================== Responses ====================

class OrdemServicoResponse(BaseModel):
    """Response com os dados da ordem de serviço"""
    id: int
    veiculo_id: str
    descricao: str
    status: str
    orcamento: Optional[float]
    observacoes: Optional[str]
    quantidade_servicos: int

    class Config:
        from_attributes = True


class CriarOrdemServicoResponse(BaseModel):
    """Response para criação de ordem de serviço"""
    id: int
    veiculo_id: str
    descricao: str
    status: str
    message: str = "Ordem de serviço criada com sucesso"


class StatusChangeResponse(BaseModel):
    """Response para mudança de status"""
    id: int
    status: str
    message: str


class ClienteResumoResponse(BaseModel):
    """Dados do cliente dono do veículo atendido pela OS"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    cpf_cnpj: Optional[str] = None
    email: Optional[str] = None


class VeiculoResumoResponse(BaseModel):
    """Dados do veículo atendido pela OS"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    placa: str
    modelo: str
    marca_id: int
    ano_fabricacao: Optional[int] = None


class InsumoResumoResponse(BaseModel):
    """Peça/insumo consumido por um serviço da OS"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    estoque: int


class ServicoItemResponse(BaseModel):
    """Um serviço adicionado à OS, com as peças que ele consome"""

    servico_id: str
    nome: Optional[str] = None
    quantidade: int
    valor_unitario: float
    valor_total: float
    insumos: list[InsumoResumoResponse] = Field(default_factory=list)


class OrdemServicoDetailResponse(BaseModel):
    """Response detalhada de uma ordem de serviço"""

    id: int
    veiculo_id: str
    descricao: str
    status: str
    orcamento: Optional[float]
    observacoes: Optional[str]
    cliente: Optional[ClienteResumoResponse]
    veiculo: Optional[VeiculoResumoResponse]
    itens: list[ServicoItemResponse]
    valor_total_itens: float


class OrdensServicoPaginadasResponse(BaseModel):
    """Response paginada da listagem de ordens de serviço"""

    itens: list[OrdemServicoResponse]
    total: int
    page: int
    page_size: int
    total_paginas: int


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
    - veiculo_id: obrigatório
    - descricao: mínimo 3 caracteres, máximo 1000
    - orcamento: opcional, deve ser positivo se informado
    """
    try:
        command = CriarOrdemServicoCommand(
            veiculo_id=request.veiculo_id,
            descricao=request.descricao,
            orcamento=request.orcamento,
            observacoes=request.observacoes,
        )

        ordem_servico = await use_case.execute(command)

        return CriarOrdemServicoResponse(
            id=ordem_servico.id,
            veiculo_id=ordem_servico.veiculo_id,
            descricao=str(ordem_servico.descricao),
            status=ordem_servico.status.value,
        )

    except VeiculoNaoEncontradoError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar ordem de serviço " + str(e),
        )


@router.get(
    "",
    response_model=OrdensServicoPaginadasResponse,
    summary="Listar Ordens de Serviço",
    description=(
        "Lista as ordens de serviço com paginação, podendo ser filtradas por "
        "status, CPF/CNPJ do cliente ou placa do veículo. "
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
    try:
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

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar ordens de serviço",
        )


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
    try:
        detalhe: OrdemServicoDetalhada | None = await use_case.execute(ordem_id)

        if detalhe is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ordem de serviço {ordem_id} não encontrada",
            )

        return _para_detail_response(detalhe)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter ordem de serviço",
        )


def _para_detail_response(
    detalhe: OrdemServicoDetalhada,
) -> OrdemServicoDetailResponse:
    ordem_servico = detalhe.ordem_servico

    return OrdemServicoDetailResponse(
        id=ordem_servico.id,
        veiculo_id=ordem_servico.veiculo_id,
        descricao=str(ordem_servico.descricao),
        status=ordem_servico.status.value,
        orcamento=ordem_servico.orcamento,
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
        itens=[_para_item_response(item) for item in detalhe.itens],
        valor_total_itens=detalhe.valor_total_itens,
    )


def _para_item_response(item: ItemServicoDetalhado) -> ServicoItemResponse:
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
    try:
        ordem_servico = await use_case.execute(
            IniciarDiagnosticoOrdemServicoCommand(
                ordem_servico_id=ordem_id,
                observacoes=request.observacoes,
            )
        )

        if ordem_servico is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ordem de serviço {ordem_id} não encontrada",
            )

        return StatusChangeResponse(
            id=ordem_servico.id,
            status=ordem_servico.status.value,
            message="Diagnóstico iniciado com sucesso",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao iniciar diagnóstico",
        )


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
    try:
        ordem_servico = await use_case.execute(
            EnviarOrdemServicoParaAprovacaoCommand(
                ordem_servico_id=ordem_id,
                orcamento=request.orcamento,
                observacoes=request.observacoes,
            )
        )

        if ordem_servico is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ordem de serviço {ordem_id} não encontrada",
            )

        return StatusChangeResponse(
            id=ordem_servico.id,
            status=ordem_servico.status.value,
            message=(
                "Ordem enviada para aprovação. "
                f"Orçamento: R$ {ordem_servico.orcamento:.2f}"
            ),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar para aprovação",
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
    use_case: CriarOrdemServicoUseCase = Depends(get_criar_ordem_servico_use_case),
    db=Depends(get_db),
):
    """Adiciona um serviço à ordem de serviço"""
    try:
        ordem_servico = await use_case.ordem_servico_repository.find_by_id(ordem_id)

        if not ordem_servico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ordem de serviço {ordem_id} não encontrada",
            )

        # Buscar o serviço no banco para recuperar o valor
        servico = db.query(ServicoModel).filter(
            ServicoModel.id == int(request.servico_id)
        ).first()

        if not servico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Serviço {request.servico_id} não encontrado",
            )

        # Adicionar item com o valor do serviço
        ordem_servico.adicionar_item(
            servico_id=request.servico_id,
            valor=float(servico.valor),
            quantidade=request.quantidade,
        )
        await use_case.ordem_servico_repository.save(ordem_servico)

        return StatusChangeResponse(
            id=ordem_servico.id,
            status=ordem_servico.status.value,
            message=f"Serviço adicionado. Total de serviços: {len(ordem_servico.itens)}",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao adicionar serviço",
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
    use_case: CriarOrdemServicoUseCase = Depends(get_criar_ordem_servico_use_case),
):
    """Remove um serviço da ordem de serviço"""
    try:
        ordem_servico = await use_case.ordem_servico_repository.find_by_id(ordem_id)

        if not ordem_servico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ordem de serviço {ordem_id} não encontrada",
            )

        ordem_servico.remover_item(request.servico_id)
        await use_case.ordem_servico_repository.save(ordem_servico)

        return StatusChangeResponse(
            id=ordem_servico.id,
            status=ordem_servico.status.value,
            message=f"Serviço removido. Total de serviços: {len(ordem_servico.itens)}",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao remover serviço",
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
    try:
        ordem_servico = await use_case.execute(
            AprovarOrcamentoOrdemServicoCommand(ordem_servico_id=ordem_id)
        )

        if ordem_servico is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ordem de serviço {ordem_id} não encontrada",
            )

        return StatusChangeResponse(
            id=ordem_servico.id,
            status=ordem_servico.status.value,
            message="Ordem aprovada e execução iniciada",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao aprovar execução",
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
    try:
        ordem_servico = await use_case.execute(
            FinalizarOrdemServicoCommand(
                ordem_servico_id=ordem_id,
                observacoes=request.observacoes,
            )
        )

        if ordem_servico is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ordem de serviço {ordem_id} não encontrada",
            )

        return StatusChangeResponse(
            id=ordem_servico.id,
            status=ordem_servico.status.value,
            message="Ordem finalizada com sucesso",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao finalizar ordem",
        )


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
    try:
        ordem_servico = await use_case.execute(
            EntregarOrdemServicoCommand(
                ordem_servico_id=ordem_id,
                observacoes=request.observacoes,
            )
        )

        if ordem_servico is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ordem de serviço {ordem_id} não encontrada",
            )

        return StatusChangeResponse(
            id=ordem_servico.id,
            status=ordem_servico.status.value,
            message="Ordem entregue com sucesso",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao entregar ordem",
        )


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
    try:
        ordem_servico = await use_case.execute(
            RetornarOrdemServicoParaDiagnosticoCommand(
                ordem_servico_id=ordem_id,
                motivo=request.motivo,
            )
        )

        if ordem_servico is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ordem de serviço {ordem_id} não encontrada",
            )

        return StatusChangeResponse(
            id=ordem_servico.id,
            status=ordem_servico.status.value,
            message="Ordem retornada para diagnóstico",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao retornar para diagnóstico",
        )
