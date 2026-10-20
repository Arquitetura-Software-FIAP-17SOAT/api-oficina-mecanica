from sqlalchemy.orm import Session

from adapters.auth.password_hasher import BCryptPasswordHasher
from adapters.database.models import ClienteModel, MarcaModel, UserModel, VeiculoModel
from adapters.database.seeders.sessao import sessao_de_seed


def _obter_ou_criar(db: Session, modelo, filtros: dict, novo, rotulo: str):
    """Devolve o registro que atende ``filtros`` ou grava ``novo`` quando não existe."""
    existente = db.query(modelo).filter_by(**filtros).first()
    if existente:
        print(f"{rotulo} ja existe")
        return existente

    db.add(novo)
    db.commit()
    db.refresh(novo)
    print(f"{rotulo} criado (ID: {novo.id})")
    return novo


def seed_cliente_veiculo(db: Session | None = None) -> None:
    """Cria um cliente de exemplo (Nilson Junior) e o veículo dele (Polo 2013)."""
    with sessao_de_seed(db) as sessao:
        usuario = _obter_ou_criar(
            sessao,
            UserModel,
            {"email": "nilson@example.com"},
            UserModel(
                nome="Nilson Junior",
                email="nilson@example.com",
                telefone="11999999999",
                senha_hash=BCryptPasswordHasher().hash("senha123"),
            ),
            "Usuario",
        )
        cliente = _obter_ou_criar(
            sessao,
            ClienteModel,
            {"usuario_id": usuario.id},
            ClienteModel(
                usuario_id=usuario.id,
                nome="Nilson Junior",
                cpf_cnpj="52998224725",
                email="nilson@example.com",
            ),
            "Cliente",
        )
        marca = _obter_ou_criar(
            sessao,
            MarcaModel,
            {"nome": "Volkswagen"},
            MarcaModel(nome="Volkswagen"),
            "Marca",
        )
        _obter_ou_criar(
            sessao,
            VeiculoModel,
            {"cliente_id": cliente.id, "modelo": "Polo", "ano_fabricacao": 2013},
            VeiculoModel(
                cliente_id=cliente.id,
                marca_id=marca.id,
                placa="ABC1234",
                chassi="9BWKK81K42A000001",
                modelo="Polo",
                ano_fabricacao=2013,
            ),
            "Veiculo",
        )
        print("\nSeed de cliente e veiculo concluido com sucesso!")
