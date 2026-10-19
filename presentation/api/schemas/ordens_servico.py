"""Schemas (requests e responses) da API de ordens de serviço."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ServicoSolicitadoRequest(BaseModel):
    """Serviço do catálogo solicitado na abertura da OS"""
    servico_id: str = Field(..., description="ID do serviço")
    quantidade: int = Field(1, description="Quantidade")


class InsumoSolicitadoRequest(BaseModel):
    """Peça/insumo solicitado na abertura da OS"""
    insumo_id: int = Field(..., description="ID do insumo")
    quantidade: int = Field(1, description="Quantidade")


class CriarOrdemServicoRequest(BaseModel):
    """Request para criar uma nova ordem de serviço"""
    veiculo_id: str = Field(..., description="ID do veículo")
    cliente_id: Optional[int] = Field(
        None,
        description=(
            "ID do cliente. Opcional: o cliente é o dono do veículo; se informado, "
            "precisa ser o dono do veículo."
        ),
    )
    servicos: list[ServicoSolicitadoRequest] = Field(
        default_factory=list, description="Serviços a executar"
    )
    insumos: list[InsumoSolicitadoRequest] = Field(
        default_factory=list,
        description="Peças/insumos a usar (dão baixa no estoque)",
    )
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


class AdicionarItemRequest(BaseModel):
    """Request para adicionar serviço à ordem"""
    servico_id: str = Field(..., description="ID do serviço")
    quantidade: int = Field(1, description="Quantidade")


class RemoverItemRequest(BaseModel):
    """Request para remover serviço da ordem"""
    servico_id: str = Field(..., description="ID do serviço a remover")


class AdicionarInsumoRequest(BaseModel):
    """Request para registrar uma peça/insumo avulso usado na ordem"""
    insumo_id: int = Field(..., description="ID do insumo")
    quantidade: int = Field(1, description="Quantidade consumida")


class RemoverInsumoRequest(BaseModel):
    """Request para remover um insumo avulso da ordem"""
    insumo_id: int = Field(..., description="ID do insumo a remover")


class FinalizarOSRequest(BaseModel):
    """Request para finalizar OS"""
    observacoes: Optional[str] = Field(None, description="Observações finais")


class EntregarOSRequest(BaseModel):
    """Request para entregar OS"""
    observacoes: Optional[str] = Field(None, description="Observações na entrega")


class RetornarDiagnosticoRequest(BaseModel):
    """Request para retornar para diagnóstico"""
    motivo: Optional[str] = Field(None, description="Motivo da devolução")


class IniciarExecucaoRequest(BaseModel):
    """Request para iniciar a execução de um serviço"""
    data_inicio: Optional[str] = Field(
        None,
        description="Data e hora de início (ISO 8601). Se omitida, usa a hora atual.",
        examples=["2025-01-15T10:30:00Z"],
    )


class FinalizarExecucaoRequest(BaseModel):
    """Request para finalizar a execução de um serviço"""
    data_fim: Optional[str] = Field(
        None,
        description="Data e hora de término (ISO 8601). Se omitida, usa a hora atual.",
        examples=["2025-01-15T12:30:00Z"],
    )


class OrdemServicoResponse(BaseModel):
    """Response com os dados da ordem de serviço"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    veiculo_id: str
    descricao: str
    status: str
    orcamento: Optional[float]
    status_orcamento: str
    observacoes: Optional[str]
    quantidade_servicos: int


class CriarOrdemServicoResponse(BaseModel):
    """Response para criação de ordem de serviço"""
    id: int
    veiculo_id: str
    descricao: str
    status: str
    quantidade_servicos: int = 0
    quantidade_insumos: int = 0
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


class InsumoUtilizadoResponse(BaseModel):
    """Uma peça/insumo avulso registrado diretamente na OS"""

    insumo_id: str
    nome: Optional[str] = None
    quantidade: int
    valor_unitario: float
    valor_total: float


class OrdemServicoDetailResponse(BaseModel):
    """Response detalhada de uma ordem de serviço"""

    id: int
    veiculo_id: str
    descricao: str
    status: str
    orcamento: Optional[float]
    status_orcamento: str
    observacoes: Optional[str]
    cliente: Optional[ClienteResumoResponse]
    veiculo: Optional[VeiculoResumoResponse]
    itens: list[ServicoItemResponse]
    insumos_utilizados: list[InsumoUtilizadoResponse]
    valor_total_itens: float


class OrdensServicoPaginadasResponse(BaseModel):
    """Response paginada da listagem de ordens de serviço"""

    itens: list[OrdemServicoResponse]
    total: int
    page: int
    page_size: int
    total_paginas: int


class ExecucaoServicoResponse(BaseModel):
    """Response para operações de execução de serviço (início e fim)"""
    ordem_servico_id: int
    servico_id: int
    data_inicio: Optional[str]
    data_fim: Optional[str]
    tempo_execucao_horas: Optional[float] = None
    mensagem: str


class TempoMedioExecucaoResponse(BaseModel):
    """Tempo médio das execuções concluídas de um serviço"""
    servico_id: int
    nome_servico: str
    tempo_medio_horas: float
    quantidade_execucoes: int
