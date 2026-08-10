-- Consultar OS
SELECT
    os.id AS ordem_servico_id,
    os.orcamento,
    os.observacoes,

    c.id AS cliente_id,
    c.nome AS cliente,
    c.cpf_cnpj,
    c.email AS cliente_email,

    v.id AS veiculo_id,
    v.placa,
    v.chassi,
    v.modelo,
    v.ano_fabricacao,

    m.id AS marca_id,
    m.nome AS marca

FROM ordens_servico os
INNER JOIN veiculos v
    ON v.id = os.veiculo_id
INNER JOIN clientes c
    ON c.id = v.cliente_id
INNER JOIN marcas m
    ON m.id = v.marca_id
WHERE os.id = 5;

-- Consultar Serviços de uma OS
SELECT
    os.id AS ordem_servico_id,
    s.id AS servico_id,
    s.nome AS servico,
    s.descricao,
    s.tempo_estimado,
    s.valor
FROM ordens_servico os
INNER JOIN ordem_servico_servicos oss
    ON oss.ordem_servico_id = os.id
INNER JOIN servicos s
    ON s.id = oss.servico_id
WHERE os.id = 5
ORDER BY s.nome;

-- Status da OS
SELECT
    os.id AS ordem_servico_id,
    sos.nome AS status,
    hos.data_status
FROM ordens_servico os
INNER JOIN historico_ordem_servico hos
    ON hos.ordem_servico_id = os.id
INNER JOIN status_ordem_servico sos
    ON sos.id = hos.status_id
WHERE os.id = 14
ORDER BY hos.data_status ASC;