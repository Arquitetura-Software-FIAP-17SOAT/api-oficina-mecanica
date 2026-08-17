from dataclasses import dataclass
from domain.value_objects.cpf_cnpj import CpfCnpj

from application.queries.get_ordem_servico_detalhada import (
    GetOrdemServicoDetalhadaUseCase,
    OrdemServicoDetalhada,
)


@dataclass
class ConsultarOrdemServicoPublicaQuery:
    """Consulta de acompanhamento feita pelo próprio cliente."""

    numero_os: int
    cpf_cnpj: str


class ConsultarOrdemServicoPublicaUseCase:
    """Caso de uso para o cliente acompanhar a própria OS, sem login administrativo.

    O enunciado separa "cliente acompanha o andamento pelo app" de "APIs
    administrativas exigem JWT". Este caso de uso atende o primeiro: em vez de
    uma sessão de funcionário, a autorização vem da posse de dois dados que só
    o dono da OS reúne — o número da ordem e o CPF/CNPJ cadastrado nela.

    Devolve ``None`` tanto quando a OS não existe quanto quando o documento não
    confere. A indistinção é proposital: se o "não encontrada" e o "não é sua"
    fossem respostas diferentes, a rota viraria um oráculo para descobrir quais
    números de OS existem e a qual documento pertencem.
    """

    def __init__(
        self, get_ordem_servico_detalhada_use_case: GetOrdemServicoDetalhadaUseCase
    ):
        self.get_ordem_servico_detalhada_use_case = get_ordem_servico_detalhada_use_case

    async def execute(
        self, query: ConsultarOrdemServicoPublicaQuery
    ) -> OrdemServicoDetalhada | None:
        documento = self._normalizar_documento(query.cpf_cnpj)

        if not documento:
            return None

        detalhe = await self.get_ordem_servico_detalhada_use_case.execute(
            query.numero_os
        )

        if detalhe is None or detalhe.cliente is None:
            return None

        if str(detalhe.cliente.cpf_cnpj or "") != documento:
            return None

        return detalhe

    @staticmethod
    def _normalizar_documento(cpf_cnpj: str | None) -> str | None:
        """Normaliza e valida CPF/CNPJ para comparação com o documento cadastrado."""
        if not cpf_cnpj:
            return None

        try:
            return str(CpfCnpj(cpf_cnpj))
        except ValueError:
            return None
