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

> Se não estiver usando um ambiente Docker, certifique-se de ter as dependências instaladas via `uv install`.
