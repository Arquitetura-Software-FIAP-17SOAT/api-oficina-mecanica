from infrastructure.database.database import SessionLocal
from infrastructure.database.models import StatusOrdemServicoModel

def seed_status_ordem_servico():
    """Popula o banco com status de Ordem de Serviço"""
    db = SessionLocal()
    
    if db.query(StatusOrdemServicoModel).count() > 0:
        print("Status já existem!")
        db.close()
        return
    
    status_list = [
        StatusOrdemServicoModel(nome="Recebida"),
        StatusOrdemServicoModel(nome="Em diagnóstico"),
        StatusOrdemServicoModel(nome="Aguardando aprovação"),
        StatusOrdemServicoModel(nome="Em execução"),
        StatusOrdemServicoModel(nome="Finalizada"),
        StatusOrdemServicoModel(nome="Entregue"),
    ]
    
    db.add_all(status_list)
    db.commit()
    print("Status inseridos com sucesso")
    db.close()

if __name__ == "__main__":
    seed_status_ordem_servico()