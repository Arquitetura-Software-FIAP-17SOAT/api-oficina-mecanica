from dataclasses import dataclass
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from sqlalchemy import and_

from infrastructure.database.models import OrdemServicoServicoModel, OrdemServicoModel


def _normalizar_utc(data: datetime) -> datetime:
    if data.tzinfo is not None:
        return data.astimezone(UTC).replace(tzinfo=None)
    return data


@dataclass
class FinalizarExecucaoServicoCommand:
    """Comando para marcar o fim da execução de um serviço em uma OS."""

    ordem_servico_id: int
    servico_id: int
    data_fim: datetime | None = None


class FinalizarExecucaoServicoUseCase:
    """Caso de uso para registrar o fim da execução de um serviço específico.
    
    Validações:
    - Ordem de serviço deve existir
    - Serviço deve estar adicionado à ordem
    - Serviço deve ter um data_inicio registrado
    - data_fim não pode ser anterior a data_inicio
    - data_fim não pode ser no futuro
    """

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, command: FinalizarExecucaoServicoCommand) -> dict:
        """Executa o comando e retorna os dados do serviço com a data_fim registrada e tempo calculado."""
        
        # Validar se ordem de serviço existe
        ordem = self.db.query(OrdemServicoModel).filter(
            OrdemServicoModel.id == command.ordem_servico_id
        ).first()
        
        if not ordem:
            raise ValueError(f"Ordem de serviço {command.ordem_servico_id} não encontrada")
        
        # Buscar o item de serviço na ordem
        item = self.db.query(OrdemServicoServicoModel).filter(
            and_(
                OrdemServicoServicoModel.ordem_servico_id == command.ordem_servico_id,
                OrdemServicoServicoModel.servico_id == command.servico_id,
            )
        ).first()
        
        if not item:
            raise ValueError(
                f"Serviço {command.servico_id} não encontrado na ordem {command.ordem_servico_id}"
            )
        
        # Validar se serviço foi iniciado
        if item.data_inicio is None:
            raise ValueError(
                f"Serviço {command.servico_id} não foi iniciado ainda"
            )
        
        # Validar se serviço já foi finalizado
        if item.data_fim is not None:
            raise ValueError(
                f"Serviço {command.servico_id} já foi finalizado em {item.data_fim}"
            )
        
        # Usar a data fornecida ou usar agora em UTC
        data_fim = _normalizar_utc(command.data_fim or datetime.now(UTC))
        
        # Validar se data_fim não é no futuro
        if data_fim > datetime.now():
            raise ValueError("A data de fim não pode ser no futuro")
        
        # Validar se data_fim não é anterior a data_inicio
        if data_fim < item.data_inicio:
            raise ValueError("A data de fim não pode ser anterior à data de início")
        
        # Atualizar data_fim
        item.data_fim = data_fim
        self.db.commit()
        
        # Calcular tempo de execução em horas
        tempo_execucao = (data_fim - item.data_inicio).total_seconds() / 3600
        
        return {
            "ordem_servico_id": item.ordem_servico_id,
            "servico_id": item.servico_id,
            "data_inicio": item.data_inicio,
            "data_fim": item.data_fim,
            "tempo_execucao_horas": round(tempo_execucao, 2),
            "mensagem": "Execução finalizada com sucesso",
        }
