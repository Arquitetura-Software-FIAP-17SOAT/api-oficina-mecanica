"""Executa os seeders: ``python -m adapters.database.seeders.executar``.

Marcas e status sempre; o cliente/veículo de exemplo (com senha conhecida) só
quando ``SEED_DADOS_EXEMPLO=true``, ou seja, em desenvolvimento.
"""

from adapters.database.database import create_tables, ler_booleano
from adapters.database.seeders.cliente_veiculo_seeder import seed_cliente_veiculo
from adapters.database.seeders.marcas_seeder import seed_marcas
from adapters.database.seeders.status_ordem_servico_seeder import (
    seed_status_ordem_servico,
)


def executar_seeds() -> None:
    """Cria as tabelas (se faltarem) e popula os dados iniciais."""
    print("Garantindo as tabelas...")
    create_tables()

    print("Iniciando seeds...\n")

    print("1. Seeding marcas de carros...")
    seed_marcas()

    print("\n2. Seeding status de ordem de servico...")
    seed_status_ordem_servico()

    if ler_booleano("SEED_DADOS_EXEMPLO"):
        print("\n3. Seeding cliente e veiculo de exemplo...")
        seed_cliente_veiculo()
    else:
        print("\n3. Dados de exemplo ignorados (defina SEED_DADOS_EXEMPLO=true para criá-los)")

    print("\nTodos os seeds foram executados com sucesso!")


if __name__ == "__main__":
    executar_seeds()
