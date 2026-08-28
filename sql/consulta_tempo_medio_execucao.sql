SELECT
    s.id AS servico_id,
    s.nome AS nome_servico,
    ROUND(
        AVG(
            EXTRACT(EPOCH FROM (oss.data_fim - oss.data_inicio)) / 3600
        )::numeric,
        2
    ) AS tempo_medio_horas,
    COUNT(*) AS quantidade_execucoes
FROM ordem_servico_servicos oss
JOIN servicos s
    ON s.id = oss.servico_id
WHERE oss.data_inicio IS NOT NULL
  AND oss.data_fim IS NOT NULL
GROUP BY s.id, s.nome
ORDER BY s.nome;
