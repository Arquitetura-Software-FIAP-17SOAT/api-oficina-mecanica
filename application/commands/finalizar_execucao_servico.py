from dataclasses import dataclass
from datetime import datetime, UTC

from domain.repositories.execucao_servico_repository import ExecucaoServicoRepository
from domain.value_objects.status_ordem_servico import StatusOrdemServico
from application.commands.iniciar_execucao_servico import (
    OrdemServicoNaoEncontradaError,
    _agora_utc,
    _normalizar_utc,
)


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

    def __init__(self, execucao_repository: ExecucaoServicoRepository):
        self.execucao_repository = execucao_repository

    async def execute(self, command: FinalizarExecucaoServicoCommand) -> dict:
        """Executa o comando e retorna os dados do serviço com a data_fim registrada e tempo calculado."""
        
        status_ordem = self.execucao_repository.find_status_ordem(
            command.ordem_servico_id
        )

        if status_ordem is None:
            raise OrdemServicoNaoEncontradaError(
                f"Ordem de serviço {command.ordem_servico_id} não encontrada"
            )

        if status_ordem != StatusOrdemServico.EM_EXECUCAO.value:
            raise ValueError("A ordem de serviço precisa estar em execução")

        item = self.execucao_repository.find_execucao(
            command.ordem_servico_id, command.servico_id
        )

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

        # Validar se data_fim não é no futuro — comparando UTC com UTC,
        # senão o caminho default falharia em servidores fora de UTC
        if data_fim > _agora_utc():
            raise ValueError("A data de fim não pode ser no futuro")
        
        # Validar se data_fim não é anterior a data_inicio
        if data_fim < item.data_inicio:
            raise ValueError("A data de fim não pode ser anterior à data de início")
        
        # Atualizar data_fim
        item.data_fim = data_fim
        self.execucao_repository.save(item)
        
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
