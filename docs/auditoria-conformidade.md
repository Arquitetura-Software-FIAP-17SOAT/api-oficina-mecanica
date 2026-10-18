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
  `application` não dependem de `infrastructure`, `presentation` nem de frameworks, e a regra é
  verificada por `tests/unit/test_arquitetura.py`.

> Legenda: 🔴 Crítico · 🟠 Lacuna · 🟡 Atenção

---

## 1. Segurança

### 🔴 Chave JWT: variável de ambiente inoperante
`.env.example` e `docker-compose.yml` definem `JWT_SECRET_KEY`, `JWT_ALGORITHM` e
`JWT_EXPIRE_MINUTES`, mas `Settings` lê `SECRET_KEY`, `ALGORITHM` e `ACCESS_TOKEN_EXPIRE_MINUTES`,
sem `env_prefix` nem alias. Configurar o `JWT_SECRET_KEY` não tem efeito: em qualquer ambiente a
aplicação assina os tokens com o segredo versionado em `infrastructure/config/config.py`, e quem
tem acesso ao código forja um token administrativo válido.

**Impacto na Fase 2:** o `Secret` do Kubernetes e o pipeline de deploy dependem de a aplicação
realmente ler a variável. Corrigir antes de escrever os manifestos.

- `infrastructure/config/config.py`, `infrastructure/config/security.py`
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

## 2. APIs da Fase 2 ainda não atendidas

### 🟠 Listagem de OS: ordenação e exclusão lógica
`GET /ordens-servico` ordena apenas por `id` decrescente e devolve todas as OS. Falta:
- ordenar por status `Em execução > Aguardando aprovação > Em diagnóstico > Recebida`;
- dentro do mesmo status, as mais antigas primeiro;
- excluir da listagem as OS `Finalizada` e `Entregue` (exclusão lógica, sem apagar do banco).

A exclusão precisa ser uma regra explícita: hoje o filtro `?status=Finalizada` consegue listar
essas OS. Definir se continua permitido para consulta administrativa ou se passa a ser vedado.

- `infrastructure/database/repositories/ordem_servico_repository_impl.py` (`list_paginado`)
- `application/queries/list_ordens_servico.py`

### 🟠 Aprovação de orçamento por notificação externa
`POST /ordens-servico/{id}/aprovar-executar` e `/rejeitar-orcamento` existem, mas ficam atrás do
JWT administrativo (`dependencies=[Depends(get_current_user)]` no router). Um serviço externo
precisa de credencial própria (token de serviço/API key vinda de `Secret`) ou de um endpoint
dedicado. Também falta decidir o contrato da notificação (aprovada/recusada, identificação da OS).

### 🟠 Atualização de status por ferramenta externa (e-mail)
Não existe nenhum mecanismo de entrada por e-mail ou equivalente. Precisa de decisão de desenho
(webhook de um provedor, endpoint que recebe o e-mail já parseado, ou fila) e de endpoint com
autenticação própria. Reutilizar os use cases de transição existentes.

### 🟡 Nomenclatura dos status no contrato da API
O enunciado da Fase 2 usa `Diagnóstico` e `Execução`; a API devolve `Em diagnóstico` e
`Em execução` (nomes da Fase 1). Confirmar com a avaliação se é aceitável ou se a consulta de
status deve expor os nomes novos.

---

## 3. Consistência de dados

### 🟡 Gravação da OS e baixa de estoque não são atômicas
Em `adicionar-insumo` e, agora, também na abertura de OS com peças, a OS e a baixa de estoque são
persistidas em commits separados. Uma falha entre os dois deixa estoque baixado sem vínculo (ou o
inverso). A validação prévia cobre os erros previsíveis, não uma falha de banco no meio.

**Correção:** uma unidade de trabalho (uma única transação/sessão com commit ao final) coordenando
os repositórios envolvidos.

- `application/commands/criar_ordem_servico.py`
- `application/commands/adicionar_insumo_ordem_servico.py`

### 🟡 Alterar itens depois do envio para aprovação
`adicionar_item` e `remover_item` só são bloqueados em `Finalizada`/`Entregue`. Com a OS em
`Aguardando aprovação`, os itens podem mudar e `orcamento` (enviado ao cliente) deixa de bater
com `orcamento_calculado`. Definir se alterar itens após o envio devolve a OS para
`Em diagnóstico`.

---

## 4. Refatoração restante (seção 1 da Fase 2)

### 🟡 Rotas com o mesmo `try/except` repetido
`ordens_servico.py` já usa `traduzir_erros` / `ordem_servico_ou_404`
(`presentation/api/error_handling.py`). Aplicar o mesmo padrão e extrair os schemas Pydantic de
`insumos.py` (437 linhas), `veiculos.py`, `clientes.py` e `servicos.py`. `ordens_servico.py` ainda
tem ~1050 linhas por concentrar schemas, conversores e endpoints; separar os schemas em módulo
próprio.

### 🟡 Scripts e seeders na raiz
- `seed.py` e `create_schema.py` ficam soltos na raiz; mover o seed para dentro de
  `infrastructure/database/` e decidir o destino de `create_schema.py`.
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

## 5. Infraestrutura e entregáveis da Fase 2 (trabalho novo)

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
2. 🟠 Listagem de OS (ordenação + exclusão lógica), com testes.
3. 🟠 Autenticação de serviço para aprovação externa e entrada de status por e-mail.
4. 🟡 Unidade de trabalho para OS + estoque.
5. 🟡 Refatoração restante das rotas, seeders e scripts da raiz.
6. Dockerfile → `/k8s` → `/infra` → CI/CD → README e vídeo.
