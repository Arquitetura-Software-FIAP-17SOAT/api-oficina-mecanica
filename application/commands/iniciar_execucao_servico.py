from dataclasses import dataclass
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from sqlalchemy import and_

from infrastructure.database.models import OrdemServicoServicoModel, OrdemServicoModel
from domain.value_objects.status_ordem_servico import StatusOrdemServico


def _normalizar_utc(data: datetime) -> datetime:
    if data.tzinfo is not None:
        return data.astimezone(UTC).replace(tzinfo=None)
    return data


@dataclass
class IniciarExecucaoServicoCommand:
    """Comando para marcar o início da execução de um serviço em uma OS."""

    ordem_servico_id: int
    servico_id: int
    data_inicio: datetime | None = None


class IniciarExecucaoServicoUseCase:
    """Caso de uso para registrar o início da execução de um serviço específico.
    
    Validações:
    - Ordem de serviço deve existir
    - Serviço deve estar adicionado à ordem
    - Serviço não pode já ter começado (data_inicio deve ser None)
    - data_inicio não pode ser no futuro
    """

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, command: IniciarExecucaoServicoCommand) -> dict:
        """Executa o comando e retorna os dados do serviço com a data_inicio registrada."""
        
        # Validar se ordem de serviço existe
        ordem = self.db.query(OrdemServicoModel).filter(
            OrdemServicoModel.id == command.ordem_servico_id
        ).first()
        
        if not ordem:
            raise ValueError(f"Ordem de serviço {command.ordem_servico_id} não encontrada")

        if ordem.status != StatusOrdemServico.EM_EXECUCAO.value:
            raise ValueError("A ordem de serviço precisa estar em execução")
        
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
        
        # Validar se serviço já foi iniciado
        if item.data_inicio is not None:
            raise ValueError(
                f"Serviço {command.servico_id} já foi iniciado em {item.data_inicio}"
            )
        
        # Usar a data fornecida ou usar agora em UTC
        data_inicio = _normalizar_utc(command.data_inicio or datetime.now(UTC))
        
        # Validar se data_inicio não é no futuro
        if data_inicio > datetime.now():
            raise ValueError("A data de início não pode ser no futuro")
        
        # Atualizar data_inicio
        item.data_inicio = data_inicio
        self.db.commit()
        
        return {
            "ordem_servico_id": item.ordem_servico_id,
            "servico_id": item.servico_id,
            "data_inicio": item.data_inicio,
            "data_fim": item.data_fim,
            "mensagem": "Execução iniciada com sucesso",
        }
