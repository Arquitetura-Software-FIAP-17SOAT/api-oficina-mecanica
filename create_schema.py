"""Script para criar o schema completo do banco de dados."""

from sqlalchemy import text
from infrastructure.database.database import engine

sql_schema = """
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    telefone VARCHAR(20),
    senha_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    nome VARCHAR(150) NOT NULL,
    cpf_cnpj VARCHAR(18),
    email VARCHAR(150),

    CONSTRAINT fk_cliente_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS marcas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS veiculos (
    id SERIAL PRIMARY KEY,
    cliente_id INT NOT NULL,
    marca_id INT NOT NULL,

    placa VARCHAR(10) NOT NULL,
    chassi VARCHAR(30),
    modelo VARCHAR(100) NOT NULL,
    ano_fabricacao INT,

    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_veiculo_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES clientes(id),

    CONSTRAINT fk_veiculo_marca
        FOREIGN KEY (marca_id)
        REFERENCES marcas(id)
);

CREATE TABLE IF NOT EXISTS servicos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    tempo_estimado VARCHAR(30),
    valor NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS insumos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    descricao TEXT,
    preco_unitario NUMERIC(10,2),
    estoque INT DEFAULT 0,
    quantidade_minima INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS servico_insumos (
    servico_id INT NOT NULL,
    insumo_id INT NOT NULL,
    quantidade INT NOT NULL,

    PRIMARY KEY (servico_id, insumo_id),

    CONSTRAINT fk_si_servico
        FOREIGN KEY (servico_id)
        REFERENCES servicos(id),

    CONSTRAINT fk_si_insumo
        FOREIGN KEY (insumo_id)
        REFERENCES insumos(id)
);

CREATE TABLE IF NOT EXISTS ordens_servico (
    id SERIAL PRIMARY KEY,
    veiculo_id INT NOT NULL,
    descricao VARCHAR(1000) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'RECEBIDA',
    orcamento NUMERIC(10,2),
    observacoes TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT fk_os_veiculo
        FOREIGN KEY (veiculo_id)
        REFERENCES veiculos(id)
);

CREATE TABLE IF NOT EXISTS ordem_servico_servicos (
    ordem_servico_id INT NOT NULL,
    servico_id INT NOT NULL,
    valor NUMERIC(10,2) NOT NULL DEFAULT 0.0,
    quantidade INT NOT NULL DEFAULT 1,
    data_adicionado TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    PRIMARY KEY (ordem_servico_id, servico_id),

    CONSTRAINT fk_oss_ordem
        FOREIGN KEY (ordem_servico_id)
        REFERENCES ordens_servico(id),

    CONSTRAINT fk_oss_servico
        FOREIGN KEY (servico_id)
        REFERENCES servicos(id)
);

CREATE TABLE IF NOT EXISTS status_ordem_servico (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS historico_ordem_servico (
    id SERIAL PRIMARY KEY,

    ordem_servico_id INT NOT NULL,
    status_id INT NOT NULL,

    data_status TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_hist_ordem
        FOREIGN KEY (ordem_servico_id)
        REFERENCES ordens_servico(id),

    CONSTRAINT fk_hist_status
        FOREIGN KEY (status_id)
        REFERENCES status_ordem_servico(id)
);
"""

if __name__ == "__main__":
    with engine.connect() as connection:
        connection.execute(text("BEGIN"))
        try:
            for statement in sql_schema.split(";"):
                statement = statement.strip()
                if statement:
                    connection.execute(text(statement))
            connection.commit()
            print("Schema criado com sucesso!")
        except Exception as e:
            connection.rollback()
            print(f"Erro ao criar schema: {e}")
