from sqlalchemy.orm import Session

from adapters.database.models import StatusOrdemServicoModel
from adapters.database.seeders.sessao import sessao_de_seed
from domain.value_objects.status_ordem_servico import StatusOrdemServico


def seed_status_ordem_servico(db: Session | None = None) -> None:
    """Popula o banco com os status de Ordem de Serviço, se a tabela estiver vazia."""
    with sessao_de_seed(db) as sessao:
        if sessao.query(StatusOrdemServicoModel).count() > 0:
            print("Status já existem!")
            return

        sessao.add_all(
            [StatusOrdemServicoModel(nome=status.value) for status in StatusOrdemServico]
        )
        sessao.commit()
        print("Status inseridos com sucesso")
