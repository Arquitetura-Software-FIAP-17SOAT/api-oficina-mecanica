from infrastructure.database.seeders.status_ordem_servico_seeder import seed_status_ordem_servico
from infrastructure.database.seeders.cliente_veiculo_seeder import seed_cliente_veiculo
from infrastructure.database.seeders.marcas_seeder import seed_marcas

if __name__ == "__main__":
    print("Iniciando seeds...\n")
    
    print("1. Seeding marcas de carros...")
    seed_marcas()
    
    print("\n2. Seeding status de ordem de servico...")
    seed_status_ordem_servico()
    
    print("\n3. Seeding cliente e veiculo...")
    seed_cliente_veiculo()
    
    print("\nTodos os seeds foram executados com sucesso!")