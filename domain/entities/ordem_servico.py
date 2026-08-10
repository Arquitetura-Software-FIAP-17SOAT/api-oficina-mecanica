from datetime import datetime, UTC
from domain.value_objects.status_ordem_servico import StatusOrdemServico
from domain.value_objects.descricao import Descricao


class OrdemServico:
    """
    Entidade rica que representa uma Ordem de Serviço.
    
    Encapsula toda a lógica de negócio e validações relacionadas
    ao ciclo de vida de uma ordem de serviço.
    """

    def __init__(
        self,
        veiculo_id: str,
        descricao: str,
        orcamento: float = None,
        observacoes: str = None,
        id: int = None,
    ):
        if not veiculo_id or not isinstance(veiculo_id, str):
            raise ValueError("ID do veículo é obrigatório e deve ser uma string")
        
        self.id = id  # Será preenchido pelo banco após salvar
        self.veiculo_id = veiculo_id
        self.descricao = Descricao(descricao)
        self.orcamento = float(orcamento) if orcamento else None
        self.observacoes = observacoes
        self.status = StatusOrdemServico.RECEBIDA
        self.data_criacao = datetime.now(UTC)
        self.data_atualizacao = datetime.now(UTC)
        self.itens = []
        self.historico_status = [
            {
                "status": StatusOrdemServico.RECEBIDA,
                "data": self.data_criacao,
                "motivo": "Ordem de serviço criada"
            }
        ]

    def adicionar_item(self, servico_id: str, valor: float, quantidade: int = 1):
        """Adiciona um item (serviço) à ordem de serviço"""
        if not servico_id:
            raise ValueError("ID do serviço é obrigatório")
        
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
        
        if valor < 0:
            raise ValueError("Valor não pode ser negativo")
        
        # Verifica se o serviço já foi adicionado
        if any(item["servico_id"] == servico_id for item in self.itens):
            raise ValueError("Este serviço já foi adicionado à ordem de serviço")
        
        self.itens.append({
            "servico_id": servico_id,
            "valor": float(valor),
            "quantidade": quantidade,
            "data_adicionado": datetime.now(UTC)
        })
        self._atualizar_timestamp()

    def remover_item(self, servico_id: str):
        """Remove um item da ordem de serviço"""
        if not any(item["servico_id"] == servico_id for item in self.itens):
            raise ValueError("Serviço não encontrado nesta ordem de serviço")
        
        self.itens = [item for item in self.itens if item["servico_id"] != servico_id]
        self._atualizar_timestamp()

    def iniciar_diagnostico(self, observacoes: str = None):
        """Transiciona a OS para 'Em diagnóstico'"""
        self._validar_transicao(StatusOrdemServico.EM_DIAGNOSTICO)
        self.status = StatusOrdemServico.EM_DIAGNOSTICO
        
        if observacoes:
            self.observacoes = observacoes
        
        self._registrar_mudanca_status(
            StatusOrdemServico.EM_DIAGNOSTICO,
            "Diagnóstico iniciado"
        )

    def enviar_para_aprovacao(self, orcamento: float, observacoes: str = None):
        """Transiciona para 'Aguardando aprovação' com orcamento definido"""
        self._validar_transicao(StatusOrdemServico.AGUARDANDO_APROVACAO)
        
        if orcamento <= 0:
            raise ValueError("Orçamento deve ser um valor positivo")
        
        self.orcamento = orcamento
        self.status = StatusOrdemServico.AGUARDANDO_APROVACAO
        
        if observacoes:
            self.observacoes = observacoes
        
        self._registrar_mudanca_status(
            StatusOrdemServico.AGUARDANDO_APROVACAO,
            "Diagnóstico concluído, enviado para aprovação"
        )

    def aprovar_e_iniciar_execucao(self):
        """Aprova a OS e inicia a execução dos serviços"""
        self._validar_transicao(StatusOrdemServico.EM_EXECUCAO)
        
        if not self.orcamento:
            raise ValueError("Orçamento deve estar definido antes de iniciar execução")
        
        if not self.itens:
            raise ValueError("A ordem de serviço deve conter pelo menos um serviço")
        
        self.status = StatusOrdemServico.EM_EXECUCAO
        self._registrar_mudanca_status(
            StatusOrdemServico.EM_EXECUCAO,
            "Ordem aprovada, iniciando execução"
        )

    def finalizar(self, observacoes: str = None):
        """Marca a OS como finalizada (serviços concluídos)"""
        self._validar_transicao(StatusOrdemServico.FINALIZADA)
        self.status = StatusOrdemServico.FINALIZADA
        
        if observacoes:
            self.observacoes = observacoes
        
        self._registrar_mudanca_status(
            StatusOrdemServico.FINALIZADA,
            "Serviços concluídos"
        )

    def entregar(self, observacoes: str = None):
        """Marca a OS como entregue ao cliente"""
        self._validar_transicao(StatusOrdemServico.ENTREGUE)
        self.status = StatusOrdemServico.ENTREGUE
        
        if observacoes:
            self.observacoes = observacoes
        
        self._registrar_mudanca_status(
            StatusOrdemServico.ENTREGUE,
            "Veículo entregue ao cliente"
        )

    def retornar_para_diagnostico(self, motivo: str = None):
        """Retorna a OS para diagnóstico (quando cliente não aprova)"""
        if self.status not in [StatusOrdemServico.AGUARDANDO_APROVACAO]:
            raise ValueError(
                f"Não é possível retornar para diagnóstico a partir do status '{self.status.value}'"
            )
        
        self.status = StatusOrdemServico.EM_DIAGNOSTICO
        motivo_registro = motivo or "Retornado para revisão de diagnóstico"
        self._registrar_mudanca_status(
            StatusOrdemServico.EM_DIAGNOSTICO,
            motivo_registro
        )

    def retornar_para_recebida(self, motivo: str = None):
        """Retorna a OS para o status inicial (para revisão completa)"""
        if self.status not in [StatusOrdemServico.EM_DIAGNOSTICO, StatusOrdemServico.AGUARDANDO_APROVACAO]:
            raise ValueError(
                f"Não é possível retornar a OS ao status 'Recebida' a partir de '{self.status.value}'"
            )
        
        self.status = StatusOrdemServico.RECEBIDA
        motivo_registro = motivo or "Retornado ao status inicial para revisão"
        self._registrar_mudanca_status(
            StatusOrdemServico.RECEBIDA,
            motivo_registro
        )

    def pode_ser_finalizada(self) -> bool:
        """Verifica se a OS pode ser finalizada"""
        return (
            self.status == StatusOrdemServico.EM_EXECUCAO and
            len(self.itens) > 0
        )

    def obter_resumo(self) -> dict:
        """Retorna um resumo das informações da OS"""
        return {
            "id": self.id,
            "veiculo_id": self.veiculo_id,
            "descricao": str(self.descricao),
            "orcamento": self.orcamento,
            "status": self.status.value,
            "status_descricao": StatusOrdemServico.descrever_status(self.status),
            "quantidade_servicos": len(self.itens),
            "data_criacao": self.data_criacao.isoformat(),
            "data_atualizacao": self.data_atualizacao.isoformat(),
        }

    def _validar_transicao(self, novo_status: StatusOrdemServico):
        """Valida se a transição de status é permitida"""
        if not self.status.pode_transicionar_para(novo_status):
            transicoes_validas = [
                s.value for s in self.status.get_transicoes_validas(self.status)
            ]
            raise ValueError(
                f"Não é possível transicionar de '{self.status.value}' para '{novo_status.value}'. "
                f"Transições válidas: {transicoes_validas}"
            )

    def _registrar_mudanca_status(self, novo_status: StatusOrdemServico, motivo: str):
        """Registra a mudança de status no histórico"""
        self.historico_status.append({
            "status": novo_status,
            "data": datetime.now(UTC),
            "motivo": motivo
        })
        self._atualizar_timestamp()

    def _atualizar_timestamp(self):
        """Atualiza o timestamp de atualização"""
        self.data_atualizacao = datetime.now(UTC)