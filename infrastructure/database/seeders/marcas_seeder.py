from infrastructure.database.database import SessionLocal
from infrastructure.database.models import MarcaModel


def seed_marcas():
    """Popula o banco com marcas de carros"""
    db = SessionLocal()
    
    if db.query(MarcaModel).count() > 0:
        print("Marcas já existem!")
        db.close()
        return
    
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
    
    db.add_all(marcas_list)
    db.commit()
    print(f"✅ {len(marcas_list)} marcas inseridas com sucesso!")
    db.close()


if __name__ == "__main__":
    seed_marcas()
