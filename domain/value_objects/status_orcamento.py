from enum import Enum


class StatusOrcamento(str, Enum):
    """Representa o estado da decisão do cliente sobre o orçamento."""

    PENDENTE = "Pendente"
    APROVADO = "Aprovado"
    REJEITADO = "Rejeitado"