from infrastructure.database.database import SessionLocal
from infrastructure.database.models import UserModel, ClienteModel, MarcaModel, VeiculoModel
from infrastructure.auth.password_hasher import BCryptPasswordHasher


def seed_cliente_veiculo():
    """
    Seed para criar um cliente (Nilson Junior) e seu veículo (Polo 2013)
    """
    db = SessionLocal()
    
    try:
        # 1. Verificar se o usuário já existe
        usuario_existente = db.query(UserModel).filter(
            UserModel.email == "nilson@example.com"
        ).first()
        
        if not usuario_existente:
            # Criar usuário
            hasher = BCryptPasswordHasher()
            usuario = UserModel(
                nome="Nilson Junior",
                email="nilson@example.com",
                telefone="11999999999",
                senha_hash=hasher.hash("senha123"),  # Senha padrão
            )
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
            print(f"Usuario criado: {usuario.nome} (ID: {usuario.id})")
        else:
            usuario = usuario_existente
            print(f"Usuario ja existe: {usuario.nome}")
        
        # 2. Verificar se o cliente já existe
        cliente_existente = db.query(ClienteModel).filter(
            ClienteModel.usuario_id == usuario.id
        ).first()
        
        if not cliente_existente:
            # Criar cliente
            cliente = ClienteModel(
                usuario_id=usuario.id,
                nome="Nilson Junior",
                cpf_cnpj="12345678900",
                email="nilson@example.com",
            )
            db.add(cliente)
            db.commit()
            db.refresh(cliente)
            print(f"Cliente criado: {cliente.nome} (ID: {cliente.id})")
        else:
            cliente = cliente_existente
            print(f"Cliente ja existe: {cliente.nome}")
        
        # 3. Verificar se a marca Volkswagen existe
        marca = db.query(MarcaModel).filter(
            MarcaModel.nome == "Volkswagen"
        ).first()
        
        if not marca:
            # Criar marca
            marca = MarcaModel(nome="Volkswagen")
            db.add(marca)
            db.commit()
            db.refresh(marca)
            print(f"Marca criada: {marca.nome} (ID: {marca.id})")
        else:
            print(f"Marca ja existe: {marca.nome}")
        
        # 4. Verificar se o veículo já existe
        veiculo_existente = db.query(VeiculoModel).filter(
            VeiculoModel.cliente_id == cliente.id,
            VeiculoModel.modelo == "Polo",
            VeiculoModel.ano_fabricacao == 2013,
        ).first()
        
        if not veiculo_existente:
            # Criar veículo
            veiculo = VeiculoModel(
                cliente_id=cliente.id,
                marca_id=marca.id,
                placa="ABC-1234",  # Placa de exemplo
                chassi="9BWKK81K42A000001",  # Chassi de exemplo
                modelo="Polo",
                ano_fabricacao=2013,
            )
            db.add(veiculo)
            db.commit()
            db.refresh(veiculo)
            print(f"Veiculo criado: {marca.nome} {veiculo.modelo} {veiculo.ano_fabricacao} (ID: {veiculo.id})")
            print(f"   Placa: {veiculo.placa}")
        else:
            veiculo = veiculo_existente
            print(f"Veiculo ja existe: {marca.nome} {veiculo.modelo} {veiculo.ano_fabricacao}")
        
        print("\nSeed de cliente e veiculo concluido com sucesso!")
        
    except Exception as e:
        db.rollback()
        print(f"Erro ao executar seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_cliente_veiculo()
