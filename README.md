# API Oficina Mecânica

Projeto de API em Python utilizando FastAPI, DDD e Clean Architecture.

## Banco de dados

O sistema utiliza **PostgreSQL** como banco de dados. A escolha se justifica por:

- **Modelo relacional com integridade referencial**: o domínio da oficina é
  fortemente relacional (clientes → veículos → ordens de serviço → serviços,
  peças e histórico de status), e as foreign keys do PostgreSQL garantem a
  consistência desses vínculos no próprio banco.
- **Transações ACID**: operações como baixa de estoque ao registrar peças em
  uma OS e as transições de status com histórico exigem atomicidade e
  consistência sob concorrência.
- **Agregações em SQL**: métricas como o tempo médio de execução por serviço
  são calculadas no próprio banco (`AVG` sobre as janelas de execução), sem
  trazer os dados para a aplicação.
- **Maturidade e ecossistema**: é open source, amplamente adotado, com
  excelente suporte no SQLAlchemy e imagem oficial leve para Docker
  (`postgres:16-alpine`), o que simplifica o `docker-compose` da entrega.

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

Configure a chave que assina os tokens JWT — ela é obrigatória e não possui
valor default (a aplicação não sobe sem ela). Crie um arquivo `.env` a partir
do exemplo e preencha `JWT_SECRET_KEY` com um valor forte:

```bash
cp .env.example .env
# gere um segredo, ex.:
openssl rand -hex 32
# e cole o valor em JWT_SECRET_KEY no .env
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
As variáveis de autenticação (`JWT_SECRET_KEY`, `JWT_ALGORITHM`,
`JWT_EXPIRE_MINUTES`) são lidas do `.env` — ver `.env.example`.

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
