from dataclasses import dataclass

from domain.entities.ordem_servico import OrdemServico
from domain.repositories.ordem_servico_repository import OrdemServicoRepository


@dataclass
class AprovarOrcamentoOrdemServicoCommand:
    """Comando para aprovar o orçamento e iniciar a execução dos serviços."""

    ordem_servico_id: int


class AprovarOrcamentoOrdemServicoUseCase:
    """Caso de uso acionado por um gatilho externo: a aprovação do cliente.

    Representa o ponto de entrada para o evento "o cliente aprovou o
    orçamento" — por exemplo, uma confirmação recebida via aplicativo ou
    API do cliente (ver ``presentation/api/routes/ordens_servico.py``).
    Ao ser executado:

    1. busca a ordem de serviço através do repositório;
    2. aplica a regra de domínio de transição 'Aguardando aprovação' →
       'Em execução' (``OrdemServico.aprovar_e_iniciar_execucao``), que
       valida que a transição é permitida e que há orçamento e itens
       cadastrados;
    3. persiste a mudança de estado através do mesmo repositório.

    Segue o padrão Command/UseCase já usado pelos demais casos de uso da
    camada de aplicação (ex.: ``UpdateClienteUseCase``,
    ``AddEstoqueUseCase``): devolve ``None`` quando a ordem não é
    encontrada — cabe à camada de apresentação transformar isso em 404 — e
    deixa propagar ``ValueError`` para violações de regra de negócio, que a
    camada de apresentação converte em 400.
    """

    def __init__(self, ordem_servico_repository: OrdemServicoRepository):
        self.ordem_servico_repository = ordem_servico_repository

    async def execute(
        self, command: AprovarOrcamentoOrdemServicoCommand
    ) -> OrdemServico | None:
        ordem_servico = await self.ordem_servico_repository.find_by_id(
            command.ordem_servico_id
        )

        if ordem_servico is None:
            return None

        ordem_servico.aprovar_e_iniciar_execucao()

        return await self.ordem_servico_repository.save(ordem_servico)
