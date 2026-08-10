"""
Script para consultar uma Ordem de Serviço com todos os seus dados relacionados
"""

from infrastructure.database.database import SessionLocal
from infrastructure.database.models import (
    OrdemServicoModel,
    VeiculoModel,
    MarcaModel,
    ClienteModel,
    UserModel,
    OrdemServicoServicoModel,
    HistoricoOrdemServicoModel,
)


def consultar_ordem_servico(ordem_id: int):
    """
    Consulta uma ordem de serviço e exibe todos os dados relacionados
    """
    db = SessionLocal()
    
    try:
        # 1. Buscar Ordem de Serviço com relacionamentos
        ordem = db.query(OrdemServicoModel).filter(
            OrdemServicoModel.id == ordem_id
        ).first()
        
        if not ordem:
            print(f"Ordem de Serviço com ID {ordem_id} não encontrada!")
            return
        
        print("\n" + "="*80)
        print(f"ORDEM DE SERVIÇO - ID: {ordem.id}")
        print("="*80)
        
        # 2. Dados do Veículo
        veiculo = ordem.veiculo
        if veiculo:
            marca = veiculo.marca
            cliente = veiculo.cliente
            usuario = cliente.usuario if cliente else None
            
            print("\nVEÍCULO:")
            print(f"   Placa: {veiculo.placa}")
            print(f"   Marca: {marca.nome if marca else 'N/A'}")
            print(f"   Modelo: {veiculo.modelo}")
            print(f"   Ano: {veiculo.ano_fabricacao}")
            print(f"   Chassi: {veiculo.chassi}")
            
            # 3. Dados do Cliente
            if cliente:
                print("\nCLIENTE:")
                print(f"   Nome: {cliente.nome}")
                print(f"   CPF/CNPJ: {cliente.cpf_cnpj}")
                print(f"   Email: {cliente.email}")
                
                # 4. Dados do Usuário
                if usuario:
                    print("\nUSUÁRIO:")
                    print(f"   Nome: {usuario.nome}")
                    print(f"   Email: {usuario.email}")
                    print(f"   Telefone: {usuario.telefone}")
        
        # 5. Dados da Ordem de Serviço
        print("\nORDEM DE SERVIÇO:")
        print(f"   Orçamento: R$ {ordem.orcamento if ordem.orcamento else 'Não definido'}")
        print(f"   Observações: {ordem.observacoes if ordem.observacoes else 'Nenhuma'}")
        
        # 6. Serviços
        servicos = db.query(OrdemServicoServicoModel).filter(
            OrdemServicoServicoModel.ordem_servico_id == ordem_id
        ).all()
        
        if servicos:
            print(f"\nSERVIÇOS ({len(servicos)}):")
            for idx, item in enumerate(servicos, 1):
                servico = item.servico
                print(f"   {idx}. {servico.nome}")
                print(f"      Valor: R$ {servico.valor}")
                print(f"      Descrição: {servico.descricao if servico.descricao else 'N/A'}")
                print(f"      Tempo Estimado: {servico.tempo_estimado if servico.tempo_estimado else 'N/A'}")
        else:
            print(f"\nSERVIÇOS: Nenhum serviço adicionado")
        
        # 7. Histórico de Status
        historico = db.query(HistoricoOrdemServicoModel).filter(
            HistoricoOrdemServicoModel.ordem_servico_id == ordem_id
        ).order_by(HistoricoOrdemServicoModel.data_status.desc()).all()
        
        if historico:
            print(f"\nHISTÓRICO DE STATUS ({len(historico)}):")
            for idx, hist in enumerate(historico, 1):
                status = hist.status
                print(f"   {idx}. {status.nome} - {hist.data_status.strftime('%d/%m/%Y %H:%M:%S')}")
        else:
            print(f"\nHISTÓRICO DE STATUS: Nenhum histórico")
        
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"Erro ao consultar: {e}")
    finally:
        db.close()


def listar_todas_ordens():
    """
    Lista todas as ordens de serviço
    """
    db = SessionLocal()
    
    try:
        ordens = db.query(OrdemServicoModel).all()
        
        if not ordens:
            print("Nenhuma ordem de servico encontrada!")
            return
        
        print("\n" + "="*80)
        print("TODAS AS ORDENS DE SERVIÇO")
        print("="*80)
        
        for ordem in ordens:
            veiculo = ordem.veiculo
            cliente = veiculo.cliente if veiculo else None
            marca = veiculo.marca if veiculo else None
            
            print(f"\nID: {ordem.id}")
            print(f"   Veículo: {marca.nome if marca else 'N/A'} {veiculo.modelo if veiculo else 'N/A'} - Placa: {veiculo.placa if veiculo else 'N/A'}")
            print(f"   Cliente: {cliente.nome if cliente else 'N/A'}")
            print(f"   Orçamento: R$ {ordem.orcamento if ordem.orcamento else 'Não definido'}")
        
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"Erro ao listar: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    # Se passar ID como argumento: python consulta_ordem_servico.py 1
    if len(sys.argv) > 1:
        try:
            ordem_id = int(sys.argv[1])
            consultar_ordem_servico(ordem_id)
        except ValueError:
            print("ID deve ser um número inteiro!")
    else:
        # Sem argumentos, lista todas
        listar_todas_ordens()
