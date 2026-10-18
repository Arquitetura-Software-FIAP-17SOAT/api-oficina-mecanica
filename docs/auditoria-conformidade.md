# Auditoria de Conformidade — api-oficina-mecanica

Estado do repositório contra os enunciados das Fases 1 e 2 (`docs/fase1-plano-de-acao.md` e
`docs/fase2-plano-de-acao.md`). O que já foi resolvido aparece só em resumo; o detalhe dos achados
corrigidos está no `git log`. Abaixo do resumo ficam **apenas os pontos em aberto**.

- **Testes:** 697 (unitários + integração), cobertura ≈ 98% nos quatro pacotes.
- **Fase 1:** requisitos funcionais implementados e testados. Pendente só o que é externo ao código
  (vídeo, Event Storming, relatório de vulnerabilidades, PDF de entrega).
- **Fase 2, código (seções 1 e 2 do plano):** concluído.

> Legenda: 🔴 Crítico · 🟡 Atenção

## Concluído

| Tema | Resumo | Onde |
|---|---|---|
| Clean Code | Erros e 404 das rotas centralizados em helpers | `presentation/api/error_handling.py` |
| Clean Architecture / Hexagonal | `infrastructure/` virou `adapters/`; `domain` e `application` não importam `adapters`, `presentation` nem frameworks (verificado por teste) | `tests/unit/test_arquitetura.py` |
| Portas e adaptadores | Hash de senha, geração e validação de JWT atrás de portas | `application/ports/`, `adapters/auth/` |
| Atomicidade | OS + baixa de estoque numa única transação (abertura de OS, adicionar e remover insumo) | `application/ports/unit_of_work.py`, `adapters/database/transaction.py` |
| Orçamento imutável em aprovação | Itens não mudam em `Aguardando aprovação`, `Finalizada` nem `Entregue` | `OrdemServico._validar_edicao_de_itens` |
| Scripts e seeders | `create_schema.py` e `seed.py` removidos da raiz (`python -m adapters.database.seeders.executar`, que cria as tabelas antes de popular); sessão segura, catálogo de marcas único, seeders testados e na cobertura; dados de exemplo (usuário com senha conhecida) só com `SEED_DADOS_EXEMPLO=true`, definido no `docker-compose.yml`; IDs de status derivados do enum | `adapters/database/seeders/` |
| Configuração da aplicação | `echo` do SQL controlado por `SQL_ECHO` (desligado por padrão); tabelas criadas na subida (`lifespan`), não ao importar o `main.py` | `adapters/database/database.py`, `main.py` |
| APIs da Fase 2 | Abertura completa de OS, consulta de status, aprovação e atualização de status por sistema externo (`X-API-Key`), listagem ordenada com exclusão lógica | `presentation/api/routes/` |

---

## 1. Segurança

### 🔴 Chave JWT: variável de ambiente inoperante
`.env.example` e `docker-compose.yml` definem `JWT_SECRET_KEY`, `JWT_ALGORITHM` e
`JWT_EXPIRE_MINUTES`, mas `Settings` lê `SECRET_KEY`, `ALGORITHM` e `ACCESS_TOKEN_EXPIRE_MINUTES`,
sem `env_prefix` nem alias. Configurar `JWT_SECRET_KEY` não tem efeito: a aplicação sempre assina
os tokens com o segredo versionado em `adapters/config/config.py`, e quem tem o código forja um
token administrativo válido.

**Impacto na Fase 2:** o `Secret` do Kubernetes e o pipeline dependem de a aplicação ler a variável.
Corrigir antes de escrever os manifestos.

**Correção:** `env_prefix="JWT_"`, `SECRET_KEY` obrigatório (a aplicação falha ao subir se faltar),
`EXPIRE_MINUTES` no lugar de `ACCESS_TOKEN_EXPIRE_MINUTES` e remover o segredo padrão do
`docker-compose.yml`.

- `adapters/config/config.py`, `adapters/config/security.py`, `.env.example`, `docker-compose.yml`

### 🟡 Sem rate limiting na consulta pública
`POST /consulta/ordens-servico` é público (número da OS + CPF/CNPJ); sem limite de tentativas a
força bruta de documentos é possível.

**Decisão:** limite por IP no `Ingress` (`limit-rps` e `limit-connections` do `ingress-nginx`),
já incluído no plano de `/k8s`. Funciona com várias réplicas sob HPA. Um limite por número de OS
exigiria Redis e só vale se o limite por IP não bastar.

---

## 2. Pontos de atenção

### 🟡 Nomenclatura dos status
O enunciado da Fase 2 escreve `Diagnóstico` e `Execução`; a API devolve `Em diagnóstico` e
`Em execução`. São os mesmos estados, só muda a grafia. Sem ação necessária.

### 🟡 Itens podem mudar durante a execução
Em `Em execução` ainda é possível acrescentar serviço ou peça (aparecem durante o trabalho) e o
total passa a divergir do orçamento aprovado. O enunciado da Fase 1 fala em "autorizar reparos
adicionais via aplicativo"; tratar isso como um novo ciclo de aprovação é uma funcionalidade
maior, fora do escopo atual.

### 🟡 Unidade de trabalho só nos fluxos de OS + estoque
Os demais casos de uso ainda dependem de cada repositório confirmar a própria escrita. Novos
fluxos que toquem mais de um agregado devem usar o mesmo `async with unit_of_work`.

### 🟡 Portas em dois lugares
Repositórios em `domain/repositories`; serviços técnicos (`PasswordHasher`, `TokenGenerator`,
`TokenDecoder`, `UnitOfWork`) em `application/ports`. Intencional; manter o critério: persistência
de agregados no domínio, serviços técnicos na aplicação.

---

## 3. Refatoração restante

### 🟡 Rotas grandes e schemas misturados com endpoints
Separar os schemas Pydantic (requests/responses) dos endpoints: `ordens_servico.py` (~1050 linhas)
e `insumos.py` (~380) concentram schemas, conversores e rotas no mesmo arquivo.

---

## 4. Infraestrutura e entregáveis da Fase 2 (trabalho novo)

Existem apenas as pastas `infra/` e `k8s/`, vazias; não há Terraform, manifestos nem pipeline de
CI/CD. Ajustes no que já existe, antes disso:

- **`Dockerfile`:** roda como root; o `CMD` executa o seed (`python -m adapters.database.seeders.executar`) a cada início de
  container, o que gera disputa entre réplicas sob HPA (migração/seed deve ser etapa à parte, como
  `Job`); sem `HEALTHCHECK`, apesar de existir `/health`; `.dockerignore` não exclui `tests/`,
  `docs/` nem `.git`. O `pip install -e .` roda sem `[build-system]`/`packages` no `pyproject.toml`
  e pode falhar na descoberta automática de pacotes: validar o build.
- **`docker-compose.yml`:** monta `.:/app` por cima da imagem (esconde o resultado real do build)
  e traz um segredo JWT como valor padrão.
- **Escalabilidade:** o vídeo precisa demonstrar a autoescala; `scripts/teste_fluxo_api.sh` pode
  servir de base para gerar múltiplas OS.
- **README:** arquitetura (componentes, infraestrutura, fluxo de deploy), execução local, deploy
  em Kubernetes, Terraform, link da collection de APIs e link do vídeo.
- **Documentação das APIs (collection):** hoje o README só cita o Swagger em
  `http://localhost:8000/docs`, que exige a aplicação rodando. Falta:
  - exportar o `openapi.json` (por script, a partir do próprio app) para `docs/`;
  - gerar a collection do Postman a partir dele;
  - uma seção "APIs" no README com os endpoints por grupo, o fluxo de autenticação (cadastro,
    login e token Bearer), as rotas públicas (`/consulta`) e as de integração externa
    (`/integracoes`, header `X-API-Key`), e os links para esses arquivos e para o `/docs`;
  - corrigir a instrução sobre `JWT_SECRET_KEY` no README, que hoje não tem efeito (ver seção 1).

---

## Ordem sugerida

1. 🔴 Corrigir a configuração do JWT (pré-requisito do `Secret` do Kubernetes).
2. 🟡 Refatoração restante: separar os schemas das rotas.
3. Dockerfile → `/k8s` → `/infra` → CI/CD → README e vídeo.
