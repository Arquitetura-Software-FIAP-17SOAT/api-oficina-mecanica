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

Caso os testes sejam executados fora do Docker, instale/sincronize primeiro as dependências:

```bash
uv sync
```
