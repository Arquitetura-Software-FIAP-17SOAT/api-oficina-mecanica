from enum import Enum


class StatusOrdemServico(str, Enum):
    """Value Object que representa os possíveis status de uma Ordem de Serviço"""
    
    RECEBIDA = "Recebida"
    EM_DIAGNOSTICO = "Em diagnóstico"
    AGUARDANDO_APROVACAO = "Aguardando aprovação"
    EM_EXECUCAO = "Em execução"
    FINALIZADA = "Finalizada"
    ENTREGUE = "Entregue"

    @staticmethod
    def get_transicoes_validas(status_atual: 'StatusOrdemServico') -> list:
        """
        Define as transições válidas para cada status.
        Garante que a OS percorra um fluxo lógico correto.
        """
        transicoes = {
            StatusOrdemServico.RECEBIDA: [
                StatusOrdemServico.EM_DIAGNOSTICO,
            ],
            StatusOrdemServico.EM_DIAGNOSTICO: [
                StatusOrdemServico.AGUARDANDO_APROVACAO,
                StatusOrdemServico.RECEBIDA,  # Pode voltar se não for aprovado
            ],
            StatusOrdemServico.AGUARDANDO_APROVACAO: [
                StatusOrdemServico.EM_EXECUCAO,
                StatusOrdemServico.EM_DIAGNOSTICO,  # Cliente não aprovou o orçamento
                StatusOrdemServico.RECEBIDA,  # Pode voltar para revisar
                StatusOrdemServico.FINALIZADA,
            ],
            StatusOrdemServico.EM_EXECUCAO: [
                StatusOrdemServico.FINALIZADA,
            ],
            StatusOrdemServico.FINALIZADA: [
                StatusOrdemServico.ENTREGUE,
            ],
            StatusOrdemServico.ENTREGUE: [],  # Estado final, sem transições
        }
        return transicoes.get(status_atual, [])

    def pode_transicionar_para(self, novo_status: 'StatusOrdemServico') -> bool:
        """Verifica se a transição de status é válida"""
        return novo_status in self.get_transicoes_validas(self)

    @staticmethod
    def descrever_status(status: 'StatusOrdemServico') -> str:
        """Retorna uma descrição legível do status"""
        descricoes = {
            StatusOrdemServico.RECEBIDA: "Ordem recebida, aguardando diagnóstico",
            StatusOrdemServico.EM_DIAGNOSTICO: "Veículo em diagnóstico",
            StatusOrdemServico.AGUARDANDO_APROVACAO: "Diagnóstico concluído, aguardando aprovação do cliente",
            StatusOrdemServico.EM_EXECUCAO: "Serviços em execução",
            StatusOrdemServico.FINALIZADA: "Serviços concluídos, pronto para entrega",
            StatusOrdemServico.ENTREGUE: "Veículo entregue ao cliente",
        }
        return descricoes.get(status, "Status desconhecido")
