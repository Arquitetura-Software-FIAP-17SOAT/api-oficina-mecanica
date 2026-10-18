# API Oficina Mecânica

Projeto de API em Python utilizando FastAPI, DDD e Clean Architecture.

## Objetivos das fases

**Fase 1 — MVP.** Back-end da oficina mecânica: gestão de ordens de serviço (OS), clientes,
veículos, serviços e peças/insumos com controle de estoque, aplicando DDD, JWT e testes
automatizados.

**Fase 2 — qualidade, resiliência e escalabilidade.** Evoluir a aplicação da Fase 1 com código
sustentável (Clean Code, Clean Architecture/Hexagonal, testes), novas APIs para a operação e
integração com sistemas externos e, em seguida, infraestrutura automatizada (Docker, Kubernetes,
Terraform e CI/CD) capaz de escalar nos horários de pico. O andamento está em
[Estado da Fase 2](#estado-da-fase-2).

## Arquitetura

O código segue Clean Architecture / Arquitetura Hexagonal. A dependência sempre aponta para dentro:

| Camada | Papel | Pode importar |
|---|---|---|
| `domain/` | Entidades, objetos de valor (CPF/CNPJ, placa, status) e contratos dos repositórios | só `domain` |
| `application/` | Casos de uso (comandos e consultas) e portas de serviços (`application/ports`: hash de senha, geração e validação de JWT, unidade de trabalho) | `domain` |
| `adapters/` | Implementações das portas: repositórios SQLAlchemy, BCrypt, JWT, configuração, seeders | `domain`, `application` |
| `presentation/` | API REST (FastAPI): rotas, schemas, conversores e composição das dependências | `application`, `domain` e, só em `presentation/dependencies`, `adapters` |

A regra é verificada automaticamente por `tests/unit/test_arquitetura.py`. Outras decisões:

- **Transação única** para o que toca mais de um agregado (abertura de OS com peças, adicionar e
  remover insumo): a OS e a baixa de estoque são confirmadas juntas ou nenhuma delas (unidade de
  trabalho em `application/ports/unit_of_work.py`).
- **Regras de negócio no domínio**: grafo de transição de status, orçamento calculado a partir dos
  serviços e peças, bloqueio de edição de itens com a OS aguardando aprovação, finalizada ou entregue.
- **Rotas enxutas**: schemas em `presentation/api/schemas/`, conversores em
  `presentation/api/mappers/` e tradução de erros em `presentation/api/error_handling.py`.

## APIs

A documentação interativa (Swagger) fica em `http://localhost:8000/docs` com a aplicação rodando.

**Autenticação.** Cadastre-se em `POST /users/register`, faça login em `POST /users/login` e envie o
token em `Authorization: Bearer <token>`. Todas as rotas abaixo, exceto as marcadas como públicas,
exigem o token.

| Grupo | Rotas principais | Acesso |
|---|---|---|
| Usuários | `POST /users/register`, `POST /users/login` | público |
| Clientes, Veículos, Serviços | CRUD em `/clientes`, `/veiculos`, `/servicos` | JWT |
| Insumos e estoque | CRUD em `/insumos`; `/insumos/estoque-baixo`; `/insumos/{id}/estoque/entrada`, `/saida` e `/ajuste` | JWT |
| Ordens de serviço | `POST /ordens-servico` (cliente, veículo, serviços e peças em uma chamada), `GET /ordens-servico` (paginada, filtros por status, CPF/CNPJ e placa), `GET /ordens-servico/{id}` | JWT |
| Ciclo da OS | `iniciar-diagnostico`, `enviar-aprovacao`, `aprovar-executar`, `rejeitar-orcamento`, `retornar-diagnostico`, `finalizar`, `entregar`; `adicionar-item`, `remover-item`, `adicionar-insumo`, `remover-insumo` (todas `POST /ordens-servico/{id}/...`) | JWT |
| Execução de serviço | `POST /ordens-servico/{id}/servicos/{servico_id}/iniciar` e `/finalizar`; `GET /ordens-servico/metricas/tempo-medio-execucao` | JWT |
| Consulta do cliente | `POST /consulta/ordens-servico` (número da OS + CPF/CNPJ) | público |
| Integrações externas | `POST /integracoes/ordens-servico/{id}/orcamento` (`aprovado`/`recusado`) e `/status` (ação enviada por uma ferramenta como e-mail) | chave `X-API-Key` |
| Saúde | `GET /health` | público |

**Ciclo de vida da OS:** `Recebida` → `Em diagnóstico` → `Aguardando aprovação` → `Em execução` →
`Finalizada` → `Entregue` (a aprovação do orçamento leva a OS a "Em execução"; a recusa, a
"Finalizada"). Em `GET /ordens-servico`, a listagem ordena por prioridade (Em execução, Aguardando
aprovação, Em diagnóstico, Recebida), com as mais antigas primeiro, e **não lista** as OS Finalizadas
e Entregues (exclusão lógica: continuam consultáveis pelo detalhe).

## Estado da Fase 2

| Item do enunciado | Situação |
|---|---|
| Clean Code | Concluído |
| Clean Architecture / Hexagonal | Concluído (regra de dependência verificada por teste) |
| Testes automatizados | Concluído: 704 testes, 99% de cobertura nos quatro pacotes |
| API de abertura de OS (cliente, veículo, serviços e peças; devolve o id) | Concluída |
| API de consulta de status da OS | Concluída |
| API de aprovação de orçamento por notificação externa | Concluída (`/integracoes`) |
| Listagem de OS (ordenação, mais antigas primeiro, exclusão lógica) | Concluída |
| Atualização de status da OS por ferramenta externa (e-mail) | Concluída (`/integracoes`) |
| Dockerfile e docker-compose revisados | Em andamento (existem e funcionam em desenvolvimento) |
| Manifestos Kubernetes (`/k8s`) | Pendente |
| Terraform (`/infra`) | Pendente |
| Pipeline de CI/CD | Pendente |
| Collection das APIs, desenho da arquitetura da infraestrutura e vídeo | Pendente |

Os detalhes de cada item, os pontos de atenção e as pendências estão em
[`docs/fase2-plano-de-acao.md`](docs/fase2-plano-de-acao.md) e
[`docs/auditoria-conformidade.md`](docs/auditoria-conformidade.md).

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

Não é preciso configurar nada para a primeira execução: o `docker-compose.yml` já traz valores de
**desenvolvimento** para as credenciais (veja "Credenciais de desenvolvimento" abaixo). Para trocá-los,
crie um arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
# em produção, gere um segredo forte para JWT_SECRET_KEY, ex.:
openssl rand -hex 32
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
### Credenciais de desenvolvimento

Valores usados quando nada é definido no `.env` — **apenas para desenvolvimento e avaliação**, nunca
para produção:

| Variável | Valor padrão no compose | Para que serve |
|---|---|---|
| `JWT_SECRET_KEY` | `segredo-jwt-somente-para-desenvolvimento` | Assina os tokens JWT. A aplicação **não sobe sem ela** (o compose a fornece) |
| `JWT_ALGORITHM` | `HS256` | Algoritmo do JWT |
| `JWT_EXPIRE_MINUTES` | `60` | Validade do token |
| `INTEGRACAO_API_KEY` | `chave-integracao-somente-para-desenvolvimento` | Cabeçalho `X-API-Key` das rotas `/integracoes` (sem ela, 503) |
| `SEED_DADOS_EXEMPLO` | `true` | Cria o cliente `nilson@example.com` (senha `senha123`) e um veículo de exemplo |
| `SQL_ECHO` | `false` | Imprime o SQL executado, para depuração |

Fora do Docker, exporte `JWT_SECRET_KEY` (ou crie o `.env`) antes de iniciar a aplicação e os testes
já definem um valor próprio.

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

## Limitações conhecidas

- **Cadastro de usuários aberto.** `POST /users/register` é público e não há perfil de
  administrador: todo usuário cadastrado recebe, no login, um JWT que vale para todas as rotas
  administrativas. Foi mantido assim por simplicidade (trabalho acadêmico, sem exigência de
  controle de perfis no enunciado). Em um ambiente real seria necessário restringir o cadastro ou
  separar perfis (administrador e cliente).
- **Itens em execução.** Com a OS em "Em execução" ainda é possível acrescentar serviços e peças;
  o total pode divergir do orçamento aprovado, porque não há um novo ciclo de aprovação do
  cliente para os adicionais.

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
  camada `application`, e implementações de adaptadores (`adapters`) testadas com
  dublês). Não tocam banco de dados nem rede.
- `tests/integration/` — testes de integração. Sobem um SQLite em memória
  com o schema real (`adapters/database/models.py`) e exercitam:
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
domínio, aplicação, adaptadores (`adapters`) e apresentação, e deixa de fora scripts
de linha de comando (`main.py`) e as interfaces
abstratas de repositório (`domain/repositories/*`), que não têm lógica
própria — a suíte mantém a cobertura acima de 80% nos domínios críticos.
