# Auditoria de Conformidade — api-oficina-mecanica

Estado do repositório contra os enunciados das Fases 1 e 2 (`docs/fase1-plano-de-acao.md` e
`docs/fase2-plano-de-acao.md`). Este documento guarda **apenas o que continua em aberto e importa
para a Fase 2**; o histórico dos achados já corrigidos foi removido (está no `git log`).

- **Branch:** `feature/fase-2-item-1-refatoracao`
- **Testes:** 620 (unitários + integração), cobertura ≈ 98% nos quatro pacotes
- **Fase 1:** todos os requisitos funcionais do enunciado estão implementados e testados —
  fluxos da OS, 6 status com grafo de transições, consulta pública do cliente, CRUDs, estoque,
  tempo médio de execução, JWT nas rotas administrativas, validação de CPF/CNPJ e placa, Swagger,
  Docker e justificativa do PostgreSQL no README. Fica pendente apenas o que é externo ao código
  (vídeo, Event Storming, relatório de vulnerabilidades, PDF de entrega).
- **Fase 2, seção 1 (código):** Clean Code e Clean Architecture concluídos. `domain` e
  `application` não dependem de `adapters`, `presentation` nem de frameworks, e a regra é
  verificada por `tests/unit/test_arquitetura.py`.

> Legenda: 🔴 Crítico · 🟠 Lacuna · 🟡 Atenção

---

## 1. Segurança

### 🔴 Chave JWT: variável de ambiente inoperante
`.env.example` e `docker-compose.yml` definem `JWT_SECRET_KEY`, `JWT_ALGORITHM` e
`JWT_EXPIRE_MINUTES`, mas `Settings` lê `SECRET_KEY`, `ALGORITHM` e `ACCESS_TOKEN_EXPIRE_MINUTES`,
sem `env_prefix` nem alias. Configurar o `JWT_SECRET_KEY` não tem efeito: em qualquer ambiente a
aplicação assina os tokens com o segredo versionado em `adapters/config/config.py`, e quem
tem acesso ao código forja um token administrativo válido.

**Impacto na Fase 2:** o `Secret` do Kubernetes e o pipeline de deploy dependem de a aplicação
realmente ler a variável. Corrigir antes de escrever os manifestos.

- `adapters/config/config.py`, `adapters/config/security.py`
- `.env.example`, `docker-compose.yml`

**Correção:** `env_prefix="JWT_"`, `SECRET_KEY` obrigatório (sem valor padrão, a aplicação falha
ao subir se faltar), `EXPIRE_MINUTES` no lugar de `ACCESS_TOKEN_EXPIRE_MINUTES`, e remover o
segredo padrão do `docker-compose.yml`.

### 🟡 Sem rate limiting na consulta pública
`POST /consulta/ordens-servico` é público e autenticado só pelo número da OS + CPF/CNPJ. Sem
limite de tentativas, a força bruta de documentos é possível. Com várias réplicas (HPA), o
contador precisa de armazenamento compartilhado (Redis ou equivalente) ou de um limite na borda
(Ingress/API gateway).

- `presentation/api/routes/consulta_publica.py`

---

## 2. APIs da Fase 2 (pontos de atenção)

### 🟡 Nomenclatura dos status (ponto de atenção)
O enunciado da Fase 2 escreve `Diagnóstico` e `Execução`; a API devolve `Em diagnóstico` e
`Em execução`. São os mesmos estados, só muda a grafia. Sem ação necessária; manter só como
observação para a apresentação.

---

## 3. Clean Architecture / Arquitetura Hexagonal (ponto de atenção da Fase 2)

### 🟡 Estrutura de camadas e nomenclatura
A pasta `infrastructure/` foi renomeada para **`adapters/`**, o termo da Arquitetura Hexagonal para
o que ela contém: as implementações das portas (repositórios SQLAlchemy, `BCryptPasswordHasher`,
`JWTTokenGenerator`), a configuração e os seeders. O nome antigo também se confundia com a pasta
`/infra` (Terraform) que o enunciado pede para a infraestrutura como código.

| Camada | Papel | Pode importar |
|---|---|---|
| `domain/` | Entidades, objetos de valor e portas dos repositórios (`domain/repositories`) | só `domain` |
| `application/` | Casos de uso e portas de serviço (`application/ports`) | `domain` |
| `adapters/` | Adaptadores que implementam as portas (banco, hash, JWT) | `domain`, `application` |
| `presentation/` | API REST (FastAPI) e composição das dependências | `application`, `domain` e, só em `presentation/dependencies`, `adapters` |

A regra de dependência (de fora para dentro) é verificada por `tests/unit/test_arquitetura.py`, que
falha se `domain` ou `application` importarem `adapters`, `presentation` ou frameworks, ou se
`presentation` usar `adapters` fora de `presentation/dependencies`.

Pontos a manter sob observação:
- `presentation/dependencies/auth_dependencies.py` importa `decode_access_token` direto de
  `adapters`; uma porta `TokenDecoder` fecharia o último desvio (hoje permitido pelo teste por
  estar na composição das dependências).
- As portas ficam em dois lugares: repositórios em `domain/repositories` e serviços
  (`PasswordHasher`, `TokenGenerator`) em `application/ports`. Intencional, mas vale manter o
  critério: persistência de agregados no domínio, serviços técnicos na aplicação.
- A unidade de trabalho (`application/ports/unit_of_work.py`, implementada em
  `adapters/database/transaction.py`) já agrupa as escritas de OS + estoque em uma transação
  (abertura de OS, `adicionar-insumo` e `remover-insumo`). Os demais casos de uso ainda dependem
  de cada repositório confirmar a própria escrita; estender o `async with unit_of_work` a novos
  fluxos que toquem mais de um agregado.
- Pastas de código fora das camadas (`seed.py`, `create_schema.py` na raiz) ainda são pendência de
  organização (seção 5).

---

## 4. Consistência de dados

### 🟡 Alterar itens depois do envio para aprovação
`adicionar_item` e `remover_item` só são bloqueados em `Finalizada`/`Entregue`. Com a OS em
`Aguardando aprovação`, os itens podem mudar e `orcamento` (enviado ao cliente) deixa de bater
com `orcamento_calculado`. Definir se alterar itens após o envio devolve a OS para
`Em diagnóstico`.

---

## 5. Refatoração restante (seção 1 da Fase 2)

### 🟡 Rotas grandes e schemas misturados com endpoints
O `try/except` e as checagens de 404 repetidos já foram removidos de todas as rotas, com os
helpers de `presentation/api/error_handling.py` (`traduzir_erros`, `traduzir_value_error`,
`encontrado_ou_404`, `exclusao_ou_404`, `ordem_servico_ou_404`). Resta separar os schemas Pydantic
(requests/responses) dos endpoints: `ordens_servico.py` tem ~1050 linhas e `insumos.py` ~380 por
concentrarem schemas, conversores e rotas no mesmo arquivo.

### 🟡 Scripts e seeders na raiz
- `seed.py` e `create_schema.py` ficam soltos na raiz; mover o seed para dentro de
  `adapters/database/` e decidir o destino de `create_schema.py`.
- `create_schema.py` mantém um DDL manual que **diverge dos models** (não cria
  `ordem_servico_insumos`, usa `'RECEBIDA'` como status padrão). `create_tables()` já cria o schema
  real; ou se remove o script ou se adota migrações (Alembic).
- O catálogo de marcas e o padrão `SessionLocal()` manual (sem `try/finally`) se repetem entre
  seeders.

### 🟡 Detalhes de infraestrutura no código
- `echo=True` em `create_engine`: imprime todo SQL em qualquer ambiente; deve ser configurável.
- `create_tables()` executa ao importar `main.py` (efeito colateral na importação).
- `presentation/dependencies/auth_dependencies.py` importa `decode_access_token` direto da
  infraestrutura; uma porta `TokenDecoder` fecharia o último desvio da regra de camadas (hoje
  permitido pelo teste de arquitetura por estar em `presentation/dependencies`).

---

## 6. Infraestrutura e entregáveis da Fase 2 (trabalho novo)

Não existem `/k8s`, `/infra` nem pipeline de CI/CD. Pontos do que já existe que precisam de
ajuste antes disso:

- **`Dockerfile`:** roda como root; o `CMD` executa `create_schema.py` e `seed.py` a cada início
  de container, o que causa disputa entre réplicas sob HPA (migração/seed deve ser uma etapa à
  parte, como `Job` no Kubernetes); sem `HEALTHCHECK`, apesar de existir `/health`; `.dockerignore`
  não exclui `tests/`, `docs/` nem `.git`.
- **`docker-compose.yml`:** monta `.:/app` por cima da imagem (bom para desenvolvimento, mas
  esconde o resultado real do build) e traz um segredo JWT como valor padrão.
- **Testes de carga/escalabilidade:** o vídeo precisa demonstrar a autoescala; `scripts/teste_fluxo_api.sh`
  pode servir de base para gerar múltiplas OS.
- **README:** atualizar com arquitetura (componentes, infraestrutura, fluxo de deploy), execução
  local, deploy em Kubernetes, Terraform, link da collection de APIs e link do vídeo.

---

## Ordem sugerida

1. 🔴 Corrigir a configuração do JWT (pré-requisito do `Secret` do Kubernetes).
2. 🟡 Refatoração restante das rotas, seeders e scripts da raiz.
3. Dockerfile → `/k8s` → `/infra` → CI/CD → README e vídeo.
