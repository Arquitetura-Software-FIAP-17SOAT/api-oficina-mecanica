import re
from dataclasses import dataclass, field

from domain.entities.ordem_servico import OrdemServico
from domain.repositories.ordem_servico_repository import OrdemServicoRepository
from domain.value_objects.status_ordem_servico import StatusOrdemServico

STATUS_VALIDOS = {status.value for status in StatusOrdemServico}


@dataclass
class ListOrdensServicoQuery:
    """Filtros e paginação para a listagem de ordens de serviço."""

    status: str | None = None
    cpf_cnpj: str | None = None
    placa: str | None = None
    page: int = 1
    page_size: int = 10


@dataclass
class OrdensServicoPaginadas:
    """Página de resultados da listagem de ordens de serviço."""

    itens: list[OrdemServico] = field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 10

    @property
    def total_paginas(self) -> int:
        if self.page_size <= 0:
            return 0

        return (self.total + self.page_size - 1) // self.page_size


class ListOrdensServicoUseCase:
    """Caso de uso para listagem paginada e filtrada de ordens de serviço."""

    PAGE_SIZE_MAXIMO = 100

    def __init__(self, ordem_servico_repository: OrdemServicoRepository):
        self.ordem_servico_repository = ordem_servico_repository

    async def execute(self, query: ListOrdensServicoQuery) -> OrdensServicoPaginadas:
        if query.status and query.status not in STATUS_VALIDOS:
            raise ValueError(
                "Status inválido. Valores aceitos: "
                f"{', '.join(sorted(STATUS_VALIDOS))}."
            )

        page = max(query.page, 1)
        page_size = min(max(query.page_size, 1), self.PAGE_SIZE_MAXIMO)
        skip = (page - 1) * page_size

        itens, total = await self.ordem_servico_repository.list_paginado(
            skip=skip,
            limit=page_size,
            status=query.status,
            cpf_cnpj=self._normalizar_documento(query.cpf_cnpj),
            placa=self._normalizar_placa(query.placa),
        )

        return OrdensServicoPaginadas(
            itens=itens, total=total, page=page, page_size=page_size
        )

    @staticmethod
    def _normalizar_documento(valor: str | None) -> str | None:
        """Remove máscara preservando letras — CNPJs alfanuméricos são válidos."""
        if not valor:
            return None

        documento = re.sub(r"[^A-Za-z0-9]", "", valor).upper()

        return documento or None

    @staticmethod
    def _normalizar_placa(valor: str | None) -> str | None:
        if not valor:
            return None

        placa = re.sub(r"[^A-Za-z0-9]", "", valor).upper()

        return placa or None
