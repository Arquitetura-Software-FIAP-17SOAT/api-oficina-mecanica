from sqlalchemy.orm import Session
from sqlalchemy import and_
from domain.entities.ordem_servico import OrdemServico
from domain.repositories.ordem_servico_repository import OrdemServicoRepository
from domain.value_objects.status_ordem_servico import StatusOrdemServico
from infrastructure.database.models import (
    ClienteModel,
    OrdemServicoModel,
    OrdemServicoServicoModel,
    HistoricoOrdemServicoModel,
    StatusOrdemServicoModel,
    VeiculoModel,
)


class OrdemServicoRepositoryImpl(OrdemServicoRepository):
    """Implementação do repositório de Ordem de Serviço usando SQLAlchemy"""
    
    # Mapeamento de status para IDs (conforme seeder)
    STATUS_TO_ID = {
        "Recebida": 1,
        "Em diagnóstico": 2,
        "Aguardando aprovação": 3,
        "Em execução": 4,
        "Finalizada": 5,
        "Entregue": 6,
    }

    def __init__(self, db: Session):
        self.db = db

    async def save(self, ordem_servico: OrdemServico) -> OrdemServico:
        """Salva uma ordem de serviço no banco de dados, incluindo seus itens e histórico"""
        is_new = ordem_servico.id is None
        
        if is_new:
            # Criar novo registro
            model = OrdemServicoModel(
                veiculo_id=ordem_servico.veiculo_id,
                descricao=str(ordem_servico.descricao),
                status=ordem_servico.status.value,
                orcamento=ordem_servico.orcamento,
                observacoes=ordem_servico.observacoes,
                data_criacao=ordem_servico.data_criacao,
                data_atualizacao=ordem_servico.data_atualizacao,
            )
            self.db.add(model)
            self.db.flush()  # Flush para obter o ID gerado
        else:
            # Atualizar registro existente
            model = self.db.query(OrdemServicoModel).filter(
                OrdemServicoModel.id == ordem_servico.id
            ).first()
            
            if model:
                model.descricao = str(ordem_servico.descricao)
                model.status = ordem_servico.status.value
                model.orcamento = ordem_servico.orcamento
                model.observacoes = ordem_servico.observacoes
                model.data_atualizacao = ordem_servico.data_atualizacao
                
                # Limpar itens existentes para re-adicionar
                self.db.query(OrdemServicoServicoModel).filter(
                    OrdemServicoServicoModel.ordem_servico_id == model.id
                ).delete()
        
        # Salvar histórico de status
        self._salvar_historico(model.id, ordem_servico.historico_status)
        
        # Salvar itens da ordem
        for item in ordem_servico.itens:
            # Verificar se o item já existe
            existing = self.db.query(OrdemServicoServicoModel).filter(
                and_(
                    OrdemServicoServicoModel.ordem_servico_id == model.id,
                    OrdemServicoServicoModel.servico_id == int(item['servico_id'])
                )
            ).first()
            
            if not existing:
                servico_model = OrdemServicoServicoModel(
                    ordem_servico_id=model.id,
                    servico_id=int(item['servico_id']),
                    valor=item.get('valor', 0.0),
                    quantidade=item.get('quantidade', 1),
                    data_adicionado=item.get('data_adicionado'),
                )
                self.db.add(servico_model)

        self.db.commit()
        self.db.refresh(model)

        # Atualiza o ID na entidade após ser inserido no banco
        ordem_servico.id = model.id

        return ordem_servico

    async def find_by_id(self, ordem_servico_id: int) -> OrdemServico | None:
        """Busca uma ordem de serviço pelo ID"""
        model = self.db.query(OrdemServicoModel).filter(
            OrdemServicoModel.id == ordem_servico_id
        ).first()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def find_by_veiculo_id(self, veiculo_id: str) -> list:
        """Busca todas as ordens de serviço de um veículo"""
        models = self.db.query(OrdemServicoModel).filter(
            OrdemServicoModel.veiculo_id == veiculo_id
        ).all()

        return [self._model_to_entity(model) for model in models]

    async def find_by_status(self, status: str) -> list:
        """Busca todas as ordens de serviço com um status específico"""
        models = self.db.query(OrdemServicoModel).filter(
            OrdemServicoModel.status == status
        ).all()

        return [self._model_to_entity(model) for model in models]

    async def list_all(self, skip: int = 0, limit: int = 10) -> list:
        """Lista todas as ordens de serviço com paginação"""
        models = self.db.query(OrdemServicoModel).offset(skip).limit(limit).all()
        return [self._model_to_entity(model) for model in models]

    async def list_paginado(
        self,
        skip: int = 0,
        limit: int = 10,
        status: str | None = None,
        cpf_cnpj: str | None = None,
        placa: str | None = None,
    ) -> tuple[list, int]:
        """Lista ordens de serviço com paginação e filtros opcionais"""
        query = self.db.query(OrdemServicoModel)

        if status:
            query = query.filter(OrdemServicoModel.status == status)

        if placa or cpf_cnpj:
            query = query.join(
                VeiculoModel, OrdemServicoModel.veiculo_id == VeiculoModel.id
            )

            if placa:
                query = query.filter(VeiculoModel.placa == placa)

            if cpf_cnpj:
                query = query.join(
                    ClienteModel, VeiculoModel.cliente_id == ClienteModel.id
                ).filter(ClienteModel.cpf_cnpj == cpf_cnpj)

        total = query.count()

        models = (
            query.order_by(OrdemServicoModel.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return [self._model_to_entity(model) for model in models], total

    async def delete(self, id: int) -> bool:
        """Deleta uma ordem de serviço"""
        model = self.db.query(OrdemServicoModel).filter(
            OrdemServicoModel.id == id
        ).first()

        if model is None:
            return False

        self.db.delete(model)
        self.db.commit()
        return True

    def _model_to_entity(self, model: OrdemServicoModel) -> OrdemServico:
        """Converte um model SQLAlchemy em uma entidade de domínio"""
        ordem_servico = OrdemServico(
            veiculo_id=str(model.veiculo_id),  # Converte int para string
            descricao=model.descricao,
            orcamento=model.orcamento,
            observacoes=model.observacoes,
            id=model.id,  # Passa o ID do banco
        )
        
        ordem_servico.status = StatusOrdemServico(model.status) if model.status else StatusOrdemServico.RECEBIDA
        ordem_servico.data_criacao = model.data_criacao
        ordem_servico.data_atualizacao = model.data_atualizacao
        
        # Carregar itens da ordem
        itens_models = self.db.query(OrdemServicoServicoModel).filter(
            OrdemServicoServicoModel.ordem_servico_id == model.id
        ).all()
        
        ordem_servico.itens = []
        for item_model in itens_models:
            ordem_servico.itens.append({
                'servico_id': str(item_model.servico_id),
                'valor': float(item_model.valor) if item_model.valor else 0.0,
                'quantidade': item_model.quantidade if item_model.quantidade else 1,
                'data_adicionado': item_model.data_adicionado,
            })
        
        # Carregar histórico de status
        historico_models = self.db.query(HistoricoOrdemServicoModel).filter(
            HistoricoOrdemServicoModel.ordem_servico_id == model.id
        ).order_by(HistoricoOrdemServicoModel.data_status).all()
        
        ordem_servico.historico_status = []
        for historico_model in historico_models:
            # Buscar o nome do status pela relação
            status_model = self.db.query(StatusOrdemServicoModel).filter(
                StatusOrdemServicoModel.id == historico_model.status_id
            ).first()
            
            ordem_servico.historico_status.append({
                "status": StatusOrdemServico(status_model.nome) if status_model else None,
                "data": historico_model.data_status,
                "motivo": "Histórico recuperado do banco"
            })
        
        return ordem_servico
    
    def _salvar_historico(self, ordem_servico_id: int, historico: list):
        """Salva o histórico de status no banco de dados"""
        # Limpar histórico existente
        self.db.query(HistoricoOrdemServicoModel).filter(
            HistoricoOrdemServicoModel.ordem_servico_id == ordem_servico_id
        ).delete()
        
        # Inserir novo histórico
        for item_historico in historico:
            status_value = item_historico['status'].value if isinstance(item_historico['status'], StatusOrdemServico) else item_historico['status']
            status_id = self.STATUS_TO_ID.get(status_value)
            
            if status_id:
                historico_model = HistoricoOrdemServicoModel(
                    ordem_servico_id=ordem_servico_id,
                    status_id=status_id,
                    data_status=item_historico.get('data'),
                )
                self.db.add(historico_model)