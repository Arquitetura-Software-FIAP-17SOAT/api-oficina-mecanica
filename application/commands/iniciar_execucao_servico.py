from dataclasses import dataclass
from datetime import datetime, UTC

from domain.repositories.execucao_servico_repository import ExecucaoServicoRepository
from domain.value_objects.status_ordem_servico import StatusOrdemServico


class OrdemServicoNaoEncontradaError(Exception):
    """Ordem de serviço não existe — mapeada para 404 na camada de apresentação."""


def _normalizar_utc(data: datetime) -> datetime:
    if data.tzinfo is not None:
        return data.astimezone(UTC).replace(tzinfo=None)
    return data


def _agora_utc() -> datetime:
    """Hora atual em UTC naive — a mesma grandeza usada nas datas persistidas."""
    return datetime.now(UTC).replace(tzinfo=None)


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

    def __init__(self, execucao_repository: ExecucaoServicoRepository):
        self.execucao_repository = execucao_repository

    async def execute(self, command: IniciarExecucaoServicoCommand) -> dict:
        """Executa o comando e retorna os dados do serviço com a data_inicio registrada."""
        
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

        # Validar se serviço já foi iniciado
        if item.data_inicio is not None:
            raise ValueError(
                f"Serviço {command.servico_id} já foi iniciado em {item.data_inicio}"
            )
        
        # Usar a data fornecida ou usar agora em UTC
        data_inicio = _normalizar_utc(command.data_inicio or datetime.now(UTC))

        # Validar se data_inicio não é no futuro — comparando UTC com UTC,
        # senão o caminho default falharia em servidores fora de UTC
        if data_inicio > _agora_utc():
            raise ValueError("A data de início não pode ser no futuro")
        
        # Atualizar data_inicio
        item.data_inicio = data_inicio
        self.execucao_repository.save(item)
        
        return {
            "ordem_servico_id": item.ordem_servico_id,
            "servico_id": item.servico_id,
            "data_inicio": item.data_inicio,
            "data_fim": item.data_fim,
            "mensagem": "Execução iniciada com sucesso",
        }
