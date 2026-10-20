from sqlalchemy.orm import Session

from adapters.database.models import MarcaModel
from adapters.database.seeders.sessao import sessao_de_seed

MARCAS = [
    # Marcas Nacionais
    "Volkswagen",
    "Fiat",
    "Ford",
    "General Motors (Chevrolet)",

    # Marcas Asiáticas
    "Toyota",
    "Honda",
    "Nissan",
    "Hyundai",
    "Kia",
    "Suzuki",
    "Mitsubishi",
    "Daihatsu",
    "Subaru",
    "Mazda",

    # Marcas Europeias
    "Renault",
    "Peugeot",
    "Citroën",
    "Jeep",
    "BMW",
    "Mercedes-Benz",
    "Audi",
    "Volvo",
    "Porsche",
    "Lamborghini",
    "Ferrari",
    "Jaguar",
    "Land Rover",
    "Rolls-Royce",
    "Bentley",
    "Maserati",
    "SEAT",
    "Skoda",
    "Opel",
    "Lada",

    # Marcas Americanas
    "Chrysler",
    "Dodge",
    "Ram",
    "GMC",
    "Cadillac",
    "Hummer",
    "Tesla",

    # Marcas Chinesas
    "BYD",
    "Geely",
    "Chery",
    "JAC",
    "Great Wall",
    "Lifan",
    "Changan",

    # Marcas Indianas
    "Tata",
    "Mahindra",
    "Maruti Suzuki",

    # Marcas de Luxo e Especiais
    "Bugatti",
    "Koenigsegg",
    "Pagani",
    "McLaren",
    "Ascari",
]


def seed_marcas(db: Session | None = None) -> None:
    """Popula o banco com marcas de carros, se ainda não houver nenhuma."""
    with sessao_de_seed(db) as sessao:
        if sessao.query(MarcaModel).count() > 0:
            print("Marcas já existem!")
            return

        sessao.add_all([MarcaModel(nome=nome) for nome in MARCAS])
        sessao.commit()
        print(f"{len(MARCAS)} marcas inseridas com sucesso!")
