from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

from infrastructure.database.database import get_db
from infrastructure.database.models import ServicoModel

from application.commands.criar_ordem_servico import (
    CriarOrdemServicoCommand,
    CriarOrdemServicoUseCase,
    VeiculoNaoEncontradoError,
)
from presentation.dependencies.dependencies import (
    get_criar_ordem_servico_use_case,
)

router = APIRouter(
    prefix="/ordens-servico",
    tags=["Ordens de Serviço"],
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
    orcamento: float = Field(..., description="Orçamento definido")
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
    "/{ordem_id}",
    response_model=OrdemServicoResponse,
    summary="Obter Ordem de Serviço",
    description="Retorna os dados de uma ordem de serviço específica",
)
async def obter_ordem_servico(
    ordem_id: int,
    use_case: CriarOrdemServicoUseCase = Depends(get_criar_ordem_servico_use_case),
):
    """
    Obtém os detalhes de uma ordem de serviço.
    
    Retorna:
    - ID da ordem
    - Informações do veículo
    - Status atual
    - Orçamento
    - Observações
    - Quantidade de serviços adicionados
    """
    try:
        ordem_servico = await use_case.ordem_servico_repository.find_by_id(ordem_id)

        if not ordem_servico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ordem de serviço {ordem_id} não encontrada",
            )

        return OrdemServicoResponse(
            id=ordem_servico.id,
            veiculo_id=ordem_servico.veiculo_id,
            descricao=str(ordem_servico.descricao),
            status=ordem_servico.status.value,
            orcamento=ordem_servico.orcamento,
            observacoes=ordem_servico.observacoes,
            quantidade_servicos=len(ordem_servico.itens),
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter ordem de serviço",
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
    use_case: CriarOrdemServicoUseCase = Depends(get_criar_ordem_servico_use_case),
):
    """Inicia o diagnóstico de uma ordem de serviço"""
    try:
        ordem_servico = await use_case.ordem_servico_repository.find_by_id(ordem_id)

        if not ordem_servico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ordem de serviço {ordem_id} não encontrada",
            )

        ordem_servico.iniciar_diagnostico(request.observacoes)
        await use_case.ordem_servico_repository.save(ordem_servico)

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
    use_case: CriarOrdemServicoUseCase = Depends(get_criar_ordem_servico_use_case),
):
    """Envia ordem de serviço para aprovação do cliente"""
    try:
        ordem_servico = await use_case.ordem_servico_repository.find_by_id(ordem_id)

        if not ordem_servico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ordem de serviço {ordem_id} não encontrada",
            )

        ordem_servico.enviar_para_aprovacao(request.orcamento, request.observacoes)
        await use_case.ordem_servico_repository.save(ordem_servico)

        return StatusChangeResponse(
            id=ordem_servico.id,
            status=ordem_servico.status.value,
            message="Ordem enviada para aprovação",
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
    use_case: CriarOrdemServicoUseCase = Depends(get_criar_ordem_servico_use_case),
):
    """Aprova a ordem de serviço e inicia a execução"""
    try:
        ordem_servico = await use_case.ordem_servico_repository.find_by_id(ordem_id)

        if not ordem_servico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ordem de serviço {ordem_id} não encontrada",
            )

        ordem_servico.aprovar_e_iniciar_execucao()
        await use_case.ordem_servico_repository.save(ordem_servico)

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
    use_case: CriarOrdemServicoUseCase = Depends(get_criar_ordem_servico_use_case),
):
    """Finaliza a ordem de serviço"""
    try:
        ordem_servico = await use_case.ordem_servico_repository.find_by_id(ordem_id)

        if not ordem_servico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ordem de serviço {ordem_id} não encontrada",
            )

        ordem_servico.finalizar(request.observacoes)
        await use_case.ordem_servico_repository.save(ordem_servico)

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
    use_case: CriarOrdemServicoUseCase = Depends(get_criar_ordem_servico_use_case),
):
    """Entrega a ordem de serviço ao cliente"""
    try:
        ordem_servico = await use_case.ordem_servico_repository.find_by_id(ordem_id)

        if not ordem_servico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ordem de serviço {ordem_id} não encontrada",
            )

        ordem_servico.entregar(request.observacoes)
        await use_case.ordem_servico_repository.save(ordem_servico)

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
    use_case: CriarOrdemServicoUseCase = Depends(get_criar_ordem_servico_use_case),
):
    """Retorna a ordem de serviço para diagnóstico"""
    try:
        ordem_servico = await use_case.ordem_servico_repository.find_by_id(ordem_id)

        if not ordem_servico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ordem de serviço {ordem_id} não encontrada",
            )

        ordem_servico.retornar_para_diagnostico(request.motivo)
        await use_case.ordem_servico_repository.save(ordem_servico)

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
