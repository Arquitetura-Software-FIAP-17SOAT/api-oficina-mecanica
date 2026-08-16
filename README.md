# API Oficina Mecânica

Projeto de API em Python usando FastAPI, DDD e Clean Architecture.

## Como construir

```bash
docker compose build
```

## Como subir

```bash
docker compose up --build
```

A API ficará disponível em `http://localhost:8000`.

## Como ver logs

Para visualizar os logs do Docker Compose:

```bash
docker compose logs -f
```

Para visualizar apenas os logs do serviço da API:

```bash
docker compose logs -f api
```

## Como parar

```bash
docker compose down
```

## Como executar os testes

```bash
uv run pytest
```

> Se não estiver usando um ambiente Docker, certifique-se de ter as dependências instaladas via `uv sync`.

Os testes ficam em `tests/`, organizados em:

- `tests/unit/` — testes unitários (entidades, value objects, casos de uso da
  camada `application`, e implementações de infraestrutura testadas com
  dublês). Não tocam banco de dados nem rede.
- `tests/integration/` — testes de integração. Sobem um SQLite em memória
  com o schema real (`infrastructure/database/models.py`) e exercitam:
  - `tests/integration/repositories/`: os repositórios SQLAlchemy fazendo
    SQL de verdade;
  - `tests/integration/api/`: as rotas FastAPI reais, ponta a ponta
    (rota → caso de uso → repositório → banco), usando `TestClient` com a
    dependência `get_db` substituída pela sessão de teste.

## Como ver o relatório de cobertura

```bash
uv run pytest --cov --cov-report=term-missing
```

Para um relatório navegável em HTML:

```bash
uv run pytest --cov --cov-report=html
open htmlcov/index.html
```

A configuração de cobertura está em `pyproject.toml`
(`[tool.coverage.run]` / `[tool.coverage.report]`). Ela cobre os pacotes de
domínio, aplicação, infraestrutura e apresentação, e deixa de fora scripts
de linha de comando (`main.py`, `seed.py`, `create_schema.py`,
`reset_marcas.py`, `consulta_ordem_servico.py`, seeders) e as interfaces
abstratas de repositório (`domain/repositories/*`), que não têm lógica
própria — a suíte mantém a cobertura acima de 80% nos domínios críticos.
