# API Oficina Mecânica

Projeto de API em Python utilizando FastAPI, DDD e Clean Architecture.

## Pré-requisitos

Para executar a aplicação utilizando Docker, é necessário ter instalado:

- Docker
- Docker Compose

## Como executar pela primeira vez

Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
```

Acesse o diretório do projeto:

```bash
cd api-oficina-mecanica
```

Suba a aplicação:

```bash
docker compose up --build
```

O Docker Compose será responsável por subir:

- API FastAPI
- PostgreSQL
- Configurações necessárias para comunicação entre a API e o banco de dados

A variável `DATABASE_URL` é configurada automaticamente pelo `docker-compose.yml`.

## Como construir

```bash
docker compose build
```

## Como subir

```bash
docker compose up --build
```

A API ficará disponível em:

```text
http://localhost:8000
```

A documentação Swagger estará disponível em:

```text
http://localhost:8000/docs
```

## Como visualizar os logs

Para visualizar os logs de todos os serviços:

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

Para remover também os volumes, incluindo os dados persistidos do PostgreSQL:

```bash
docker compose down -v
```

> Atenção: o comando acima remove os dados armazenados no banco PostgreSQL local.

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
