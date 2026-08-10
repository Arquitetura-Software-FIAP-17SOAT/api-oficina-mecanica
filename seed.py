from infrastructure.database.seeders.status_ordem_servico_seeder import seed_status_ordem_servico
from infrastructure.database.seeders.cliente_veiculo_seeder import seed_cliente_veiculo
from infrastructure.database.seeders.marcas_seeder import seed_marcas

if __name__ == "__main__":
    print("🌱 Iniciando seeds...\n")
    
    print("1️⃣  Seeding marcas de carros...")
    seed_marcas()
    
    print("\n2️⃣  Seeding status de ordem de serviço...")
    seed_status_ordem_servico()
    
    print("\n3️⃣  Seeding cliente e veículo...")
    seed_cliente_veiculo()
    
    print("\n✅ Todos os seeds foram executados com sucesso!")