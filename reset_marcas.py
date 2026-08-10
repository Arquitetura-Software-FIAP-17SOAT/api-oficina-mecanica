from infrastructure.database.database import SessionLocal
from infrastructure.database.models import MarcaModel


def reset_marcas():
    """Reseta e popula o banco com todas as marcas de carros"""
    db = SessionLocal()
    
    marcas_list = [
        # Marcas Nacionais
        MarcaModel(nome="Volkswagen"),
        MarcaModel(nome="Fiat"),
        MarcaModel(nome="Ford"),
        MarcaModel(nome="General Motors (Chevrolet)"),
        
        # Marcas Asiáticas
        MarcaModel(nome="Toyota"),
        MarcaModel(nome="Honda"),
        MarcaModel(nome="Nissan"),
        MarcaModel(nome="Hyundai"),
        MarcaModel(nome="Kia"),
        MarcaModel(nome="Suzuki"),
        MarcaModel(nome="Mitsubishi"),
        MarcaModel(nome="Daihatsu"),
        MarcaModel(nome="Subaru"),
        MarcaModel(nome="Mazda"),
        
        # Marcas Europeias
        MarcaModel(nome="Renault"),
        MarcaModel(nome="Peugeot"),
        MarcaModel(nome="Citroën"),
        MarcaModel(nome="Jeep"),
        MarcaModel(nome="BMW"),
        MarcaModel(nome="Mercedes-Benz"),
        MarcaModel(nome="Audi"),
        MarcaModel(nome="Volvo"),
        MarcaModel(nome="Porsche"),
        MarcaModel(nome="Lamborghini"),
        MarcaModel(nome="Ferrari"),
        MarcaModel(nome="Jaguar"),
        MarcaModel(nome="Land Rover"),
        MarcaModel(nome="Rolls-Royce"),
        MarcaModel(nome="Bentley"),
        MarcaModel(nome="Maserati"),
        MarcaModel(nome="SEAT"),
        MarcaModel(nome="Skoda"),
        MarcaModel(nome="Opel"),
        MarcaModel(nome="Lada"),
        
        # Marcas Americanas
        MarcaModel(nome="Chrysler"),
        MarcaModel(nome="Dodge"),
        MarcaModel(nome="Ram"),
        MarcaModel(nome="GMC"),
        MarcaModel(nome="Cadillac"),
        MarcaModel(nome="Hummer"),
        MarcaModel(nome="Tesla"),
        
        # Marcas Chinesas
        MarcaModel(nome="BYD"),
        MarcaModel(nome="Geely"),
        MarcaModel(nome="Chery"),
        MarcaModel(nome="JAC"),
        MarcaModel(nome="Great Wall"),
        MarcaModel(nome="Lifan"),
        MarcaModel(nome="Changan"),
        
        # Marcas Indianas
        MarcaModel(nome="Tata"),
        MarcaModel(nome="Mahindra"),
        MarcaModel(nome="Maruti Suzuki"),
        
        # Marcas de Luxo e Especiais
        MarcaModel(nome="Bugatti"),
        MarcaModel(nome="Koenigsegg"),
        MarcaModel(nome="Pagani"),
        MarcaModel(nome="McLaren"),
        MarcaModel(nome="Ascari"),
    ]
    
    # Verificar quais marcas já existem
    existing_names = {marca.nome for marca in db.query(MarcaModel.nome).all()}
    marcas_to_add = [marca for marca in marcas_list if marca.nome not in existing_names]
    
    if not marcas_to_add:
        print("✅ Todas as marcas já existem no banco!")
        total = db.query(MarcaModel).count()
        print(f"📋 Total de marcas cadastradas: {total}")
        db.close()
        return
    
    db.add_all(marcas_to_add)
    db.commit()
    total = db.query(MarcaModel).count()
    print(f"✅ {len(marcas_to_add)} novas marcas inseridas!")
    print(f"📋 Total de marcas cadastradas: {total}")
    db.close()


if __name__ == "__main__":
    print("🌱 Resetando marcas de carros...\n")
    reset_marcas()
