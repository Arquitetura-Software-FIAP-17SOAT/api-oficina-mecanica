# API Oficina Mecânica

API em Python (FastAPI) para a gestão de uma oficina mecânica: ordens de serviço, clientes,
veículos, serviços e peças com controle de estoque. Usa DDD, Clean Architecture e PostgreSQL.

## Objetivos

- **Fase 1 — MVP:** back-end da oficina com JWT, validação de CPF/CNPJ e placa e testes
  automatizados.
- **Fase 2 — qualidade, resiliência e escalabilidade:** código sustentável (Clean Code, Clean
  Architecture/Hexagonal), APIs para a operação e integração com sistemas externos e, em seguida,
  infraestrutura automatizada (Docker, Kubernetes, Terraform e CI/CD). Andamento em
  [Estado da Fase 2](#estado-da-fase-2).

Detalhes: [`docs/fase1-plano-de-acao.md`](docs/fase1-plano-de-acao.md),
[`docs/fase2-plano-de-acao.md`](docs/fase2-plano-de-acao.md) e
[`docs/auditoria-conformidade.md`](docs/auditoria-conformidade.md).

## Como executar

Pré-requisitos: Docker e Docker Compose.

```bash
git clone <URL_DO_REPOSITORIO>
cd api-oficina-mecanica
docker compose up --build
```

Não é preciso configurar nada: o `docker-compose.yml` já traz credenciais de **desenvolvimento**
(tabela abaixo). Para trocá-las, copie `.env.example` para `.env` e edite (em produção, gere o
segredo com `openssl rand -hex 32`).

- API: <http://localhost:8000> · Swagger: <http://localhost:8000/docs>
- Logs: `docker compose logs -f api`
- Parar: `docker compose down` (use `-v` para apagar também os dados do PostgreSQL)

| Variável | Padrão no compose | Para que serve |
|---|---|---|
| `JWT_SECRET_KEY` | `segredo-jwt-somente-para-desenvolvimento` | Assina os tokens JWT; a aplicação **não sobe sem ela** |
| `JWT_ALGORITHM` / `JWT_EXPIRE_MINUTES` | `HS256` / `60` | Algoritmo e validade do token |
| `INTEGRACAO_API_KEY` | `chave-integracao-somente-para-desenvolvimento` | Cabeçalho `X-API-Key` das rotas `/integracoes` (sem ela, 503) |
| `SEED_DADOS_EXEMPLO` | `true` | Cria o cliente `nilson@example.com` (senha `senha123`) e um veículo de exemplo |
| `SQL_ECHO` | `false` | Imprime o SQL executado, para depuração |

Esses valores servem apenas para desenvolvimento e avaliação. Fora do Docker, exporte
`JWT_SECRET_KEY` (ou crie o `.env`) antes de iniciar a aplicação.

## Arquitetura

Clean Architecture / Arquitetura Hexagonal; a dependência sempre aponta para dentro:

| Camada | Papel | Pode importar |
|---|---|---|
| `domain/` | Entidades, objetos de valor (CPF/CNPJ, placa, status) e contratos dos repositórios | só `domain` |
| `application/` | Casos de uso e portas de serviços (`application/ports`: hash de senha, JWT, unidade de trabalho) | `domain` |
| `adapters/` | Implementações das portas: repositórios SQLAlchemy, BCrypt, JWT, configuração, seeders | `domain`, `application` |
| `presentation/` | API REST (rotas, schemas, conversores) e composição das dependências | `application`, `domain` e, só em `presentation/dependencies`, `adapters` |

A regra é verificada por `tests/unit/test_arquitetura.py`. A abertura de OS com peças e o
adicionar/remover insumo gravam a OS e a baixa de estoque numa **única transação**.

## APIs

Documentação interativa em `/docs`. Cadastre-se em `POST /users/register`, faça login em
`POST /users/login` e envie `Authorization: Bearer <token>`.

| Grupo | Rotas | Acesso |
|---|---|---|
| Usuários | `POST /users/register`, `POST /users/login` | público |
| Clientes, veículos, serviços | CRUD em `/clientes`, `/veiculos`, `/servicos` | JWT |
| Insumos e estoque | CRUD em `/insumos`, `/insumos/estoque-baixo`, `/insumos/{id}/estoque/entrada`, `/saida`, `/ajuste` | JWT |
| Ordens de serviço | `POST /ordens-servico` (cliente, veículo, serviços e peças em uma chamada), `GET /ordens-servico` (paginada; filtros por status, CPF/CNPJ e placa), `GET /ordens-servico/{id}` | JWT |
| Ciclo da OS | `POST /ordens-servico/{id}/` + `iniciar-diagnostico`, `enviar-aprovacao`, `aprovar-executar`, `rejeitar-orcamento`, `retornar-diagnostico`, `finalizar`, `entregar`, `adicionar-item`, `remover-item`, `adicionar-insumo`, `remover-insumo` | JWT |
| Execução e métricas | `POST /ordens-servico/{id}/servicos/{servico_id}/iniciar` e `/finalizar`; `GET /ordens-servico/metricas/tempo-medio-execucao` | JWT |
| Consulta do cliente | `POST /consulta/ordens-servico` (número da OS + CPF/CNPJ) | público |
| Integrações externas | `POST /integracoes/ordens-servico/{id}/orcamento` (`aprovado`/`recusado`) e `/status` (ação enviada por uma ferramenta como e-mail) | `X-API-Key` |
| Saúde | `GET /health` | público |

**Ciclo da OS:** `Recebida` → `Em diagnóstico` → `Aguardando aprovação` → `Em execução` →
`Finalizada` → `Entregue` (aprovar o orçamento leva a "Em execução"; recusar, a "Finalizada").
A listagem ordena por prioridade (Em execução, Aguardando aprovação, Em diagnóstico, Recebida), com
as mais antigas primeiro, e **não lista** as OS Finalizadas e Entregues (exclusão lógica: seguem
consultáveis pelo detalhe).

## Banco de dados

**PostgreSQL**, pelos motivos:

- **Modelo relacional com integridade referencial:** clientes → veículos → ordens de serviço →
  serviços, peças e histórico de status; as foreign keys garantem a consistência no próprio banco.
- **Transações ACID:** baixa de estoque ao registrar peças em uma OS e transições de status com
  histórico exigem atomicidade e consistência sob concorrência.
- **Agregações em SQL:** métricas como o tempo médio de execução por serviço são calculadas no banco.
- **Maturidade e ecossistema:** open source, bom suporte no SQLAlchemy e imagem oficial leve
  (`postgres:16-alpine`) para o Docker Compose.

## Testes e cobertura

```bash
uv sync                                   # instala as dependências (fora do Docker)
uv run pytest                             # roda a suíte
uv run pytest --cov --cov-report=term-missing   # com cobertura (use html para um relatório navegável)
```

- `tests/unit/`: entidades, objetos de valor, casos de uso e adaptadores, sem banco nem rede.
- `tests/integration/`: SQLite em memória com o schema real; repositórios (`repositories/`) e rotas
  ponta a ponta com `TestClient` (`api/`).

São 704 testes, com 99% de cobertura nos quatro pacotes (mínimo exigido: 80% nos domínios críticos).
A configuração está em `pyproject.toml`; ficam de fora só `main.py` e as interfaces abstratas
`domain/repositories/*`.

## Estado da Fase 2

A configuração em `terraform/` prepara a rede AWS e um bucket S3 para uso futuro
como backend; ainda não provisiona Kubernetes. As sub-redes têm rota padrão pelo
Internet Gateway. O bucket usa o nome `<projeto>-tfstate-<conta>-<região>`, com
versionamento, criptografia e bloqueio público. Execute `terraform init`,
`terraform validate` e `terraform plan` nessa pasta e revise antes de aplicar.
O estado permanece **local**: criar o bucket não o migra automaticamente.
Guarde o estado e, caso decida migrar depois, faça backup e configure o backend
com o nome obtido por `terraform output -raw state_bucket_name`, usando
`terraform init -migrate-state`.

| Item do enunciado | Situação |
|---|---|
| Clean Code, Clean Architecture/Hexagonal e testes automatizados | Concluído |
| APIs: abertura de OS, consulta de status, aprovação de orçamento externa, listagem ordenada com exclusão lógica e atualização de status por ferramenta externa | Concluído |
| Dockerfile e docker-compose revisados | Em andamento (funcionam em desenvolvimento) |
| Manifestos Kubernetes (`/k8s`), Terraform (`/infra`) e pipeline de CI/CD | Pendente |
| Collection das APIs, desenho da infraestrutura e vídeo | Pendente |

## Limitações conhecidas

- **Cadastro de usuários aberto:** `POST /users/register` é público e não há perfis; todo usuário
  cadastrado recebe um JWT válido para as rotas administrativas. Mantido por simplicidade (trabalho
  acadêmico); um ambiente real exigiria restringir o cadastro ou separar perfis.
- **Itens em execução:** com a OS "Em execução" ainda é possível acrescentar serviços e peças, e o
  total pode divergir do orçamento aprovado (não há novo ciclo de aprovação para os adicionais).
