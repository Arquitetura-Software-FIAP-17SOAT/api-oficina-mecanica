from datetime import datetime

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    TIMESTAMP,
    func,
)
from sqlalchemy.orm import relationship

from infrastructure.database.database import Base


class UserModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    telefone = Column(String(20), nullable=True)
    senha_hash = Column(String(255), nullable=False)

    clientes = relationship("ClienteModel", back_populates="usuario")


class ClienteModel(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nome = Column(String(150), nullable=False)
    cpf_cnpj = Column(String(18), nullable=True)
    email = Column(String(150), nullable=True)

    usuario = relationship("UserModel", back_populates="clientes")
    veiculos = relationship("VeiculoModel", back_populates="cliente")


class MarcaModel(Base):
    __tablename__ = "marcas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)

    veiculos = relationship("VeiculoModel", back_populates="marca")


class VeiculoModel(Base):
    __tablename__ = "veiculos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    marca_id = Column(Integer, ForeignKey("marcas.id"), nullable=False)
    placa = Column(String(10), nullable=False)
    chassi = Column(String(30), nullable=True)
    modelo = Column(String(100), nullable=False)
    ano_fabricacao = Column(Integer, nullable=True)
    criado_em = Column(TIMESTAMP, server_default=func.now())

    cliente = relationship("ClienteModel", back_populates="veiculos")
    marca = relationship("MarcaModel", back_populates="veiculos")
    ordens_servico = relationship("OrdemServicoModel", back_populates="veiculo")


class ServicoModel(Base):
    __tablename__ = "servicos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    tempo_estimado = Column(String(30), nullable=True)
    valor = Column(Numeric(10, 2), nullable=False)

    servico_insumos = relationship("ServicoInsumoModel", back_populates="servico")
    ordem_servico_servicos = relationship("OrdemServicoServicoModel", back_populates="servico")


class InsumoModel(Base):
    __tablename__ = "insumos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    descricao = Column(Text, nullable=True)
    preco_unitario = Column(Numeric(10, 2), nullable=True)
    estoque = Column(Integer, default=0)
    quantidade_minima = Column(Integer, default=0)

    servico_insumos = relationship("ServicoInsumoModel", back_populates="insumo")
    ordem_servico_insumos = relationship(
        "OrdemServicoInsumoModel", back_populates="insumo"
    )


class ServicoInsumoModel(Base):
    __tablename__ = "servico_insumos"

    servico_id = Column(Integer, ForeignKey("servicos.id"), primary_key=True)
    insumo_id = Column(Integer, ForeignKey("insumos.id"), primary_key=True)
    quantidade = Column(Integer, nullable=False)

    servico = relationship("ServicoModel", back_populates="servico_insumos")
    insumo = relationship("InsumoModel", back_populates="servico_insumos")


class OrdemServicoModel(Base):
    __tablename__ = "ordens_servico"

    id = Column(Integer, primary_key=True, index=True)
    veiculo_id = Column(Integer, ForeignKey("veiculos.id"), nullable=False)
    descricao = Column(String(1000), nullable=False)
    status = Column(String(50), nullable=False, default="RECEBIDA")
    orcamento = Column(Numeric(10, 2), nullable=True)
    observacoes = Column(Text, nullable=True)
    data_criacao = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    data_atualizacao = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    veiculo = relationship("VeiculoModel", back_populates="ordens_servico")
    ordem_servico_servicos = relationship("OrdemServicoServicoModel", back_populates="ordem_servico")
    ordem_servico_insumos = relationship(
        "OrdemServicoInsumoModel", back_populates="ordem_servico"
    )
    historico = relationship("HistoricoOrdemServicoModel", back_populates="ordem_servico")


class OrdemServicoServicoModel(Base):
    __tablename__ = "ordem_servico_servicos"

    ordem_servico_id = Column(Integer, ForeignKey("ordens_servico.id"), primary_key=True)
    servico_id = Column(Integer, ForeignKey("servicos.id"), primary_key=True)
    valor = Column(Numeric(10, 2), nullable=False, default=0.0)
    quantidade = Column(Integer, nullable=False, default=1)
    data_adicionado = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    ordem_servico = relationship("OrdemServicoModel", back_populates="ordem_servico_servicos")
    servico = relationship("ServicoModel", back_populates="ordem_servico_servicos")


class OrdemServicoInsumoModel(Base):
    """Peça/insumo avulso registrado diretamente numa ordem de serviço.

    Independente da composição fixa de um serviço (``ServicoInsumoModel``) —
    é para o consumo de peças fora da receita pré-cadastrada.
    """

    __tablename__ = "ordem_servico_insumos"

    ordem_servico_id = Column(Integer, ForeignKey("ordens_servico.id"), primary_key=True)
    insumo_id = Column(Integer, ForeignKey("insumos.id"), primary_key=True)
    valor = Column(Numeric(10, 2), nullable=False, default=0.0)
    quantidade = Column(Integer, nullable=False, default=1)
    data_adicionado = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    ordem_servico = relationship("OrdemServicoModel", back_populates="ordem_servico_insumos")
    insumo = relationship("InsumoModel", back_populates="ordem_servico_insumos")


class StatusOrdemServicoModel(Base):
    __tablename__ = "status_ordem_servico"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False)

    historico = relationship("HistoricoOrdemServicoModel", back_populates="status")


class HistoricoOrdemServicoModel(Base):
    __tablename__ = "historico_ordem_servico"

    id = Column(Integer, primary_key=True, index=True)
    ordem_servico_id = Column(Integer, ForeignKey("ordens_servico.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("status_ordem_servico.id"), nullable=False)
    data_status = Column(TIMESTAMP, server_default=func.now())

    ordem_servico = relationship("OrdemServicoModel", back_populates="historico")
    status = relationship("StatusOrdemServicoModel", back_populates="historico")
