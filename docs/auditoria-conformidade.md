# Auditoria de Conformidade — api-oficina-mecanica

Estado do repositório contra os enunciados das Fases 1 e 2 (`docs/fase1-plano-de-acao.md` e
`docs/fase2-plano-de-acao.md`). O que já foi resolvido aparece só em resumo; o detalhe dos achados
corrigidos está no `git log`. Abaixo do resumo ficam **apenas os pontos em aberto**.

- **Testes:** 704 (unitários + integração), cobertura ≈ 98% nos quatro pacotes.
- **Fase 1:** requisitos funcionais implementados e testados. Pendente só o que é externo ao código
  (vídeo, Event Storming, relatório de vulnerabilidades, PDF de entrega).
- **Fase 2, código (seções 1 e 2 do plano):** concluído.
- **Revisão geral de 2026-10-18:** planos das Fases 1 e 2 conferidos contra o código; itens marcados
  com a evidência. Fica pendente o que não se verifica pelo código (acesso do repositório a
  `soat-architecture`, build das imagens Docker, entregáveis da seção 4 da Fase 1).

> Legenda: 🔴 Crítico · 🟡 Atenção

## Concluído

| Tema | Resumo | Onde |
|---|---|---|
| Clean Code | Erros e 404 das rotas centralizados em helpers | `presentation/api/error_handling.py` |
| Clean Architecture / Hexagonal | `infrastructure/` virou `adapters/`; `domain` e `application` não importam `adapters`, `presentation` nem frameworks (verificado por teste) | `tests/unit/test_arquitetura.py` |
| Portas e adaptadores | Hash de senha, geração e validação de JWT atrás de portas | `application/ports/`, `adapters/auth/` |
| Atomicidade | OS + baixa de estoque numa única transação (abertura de OS, adicionar e remover insumo) | `application/ports/unit_of_work.py`, `adapters/database/transaction.py` |
| Orçamento imutável em aprovação | Itens não mudam em `Aguardando aprovação`, `Finalizada` nem `Entregue` | `OrdemServico._validar_edicao_de_itens` |
| Chave JWT | Lida de `JWT_SECRET_KEY`/`JWT_ALGORITHM`/`JWT_EXPIRE_MINUTES` (também do `.env`), obrigatória e sem valor padrão no código; o compose traz valores públicos de desenvolvimento, documentados no README | `adapters/config/config.py`, `docker-compose.yml` |
| Schemas das rotas | Requests/responses de OS e insumos em `presentation/api/schemas/`, conversores de OS em `presentation/api/mappers/`; `openapi.json` idêntico ao anterior | `presentation/api/` |
| Scripts e seeders | `create_schema.py` e `seed.py` removidos da raiz (`python -m adapters.database.seeders.executar`, que cria as tabelas antes de popular); sessão segura, catálogo de marcas único, seeders testados e na cobertura; dados de exemplo (usuário com senha conhecida) só com `SEED_DADOS_EXEMPLO=true`, definido no `docker-compose.yml`; IDs de status derivados do enum | `adapters/database/seeders/` |
| Configuração da aplicação | `echo` do SQL controlado por `SQL_ECHO` (desligado por padrão); tabelas criadas na subida (`lifespan`), não ao importar o `main.py` | `adapters/database/database.py`, `main.py` |
| APIs da Fase 2 | Abertura completa de OS, consulta de status, aprovação e atualização de status por sistema externo (`X-API-Key`), listagem ordenada com exclusão lógica | `presentation/api/routes/` |

---

## 1. Segurança

### 🟡 Cadastro de usuários aberto
`POST /users/register` é público e qualquer usuário cadastrado recebe, no login, um JWT que vale
para todas as rotas administrativas: não há conceito de perfil/administrador. Na prática, a
autenticação JWT existe, mas qualquer visitante pode obtê-la. Opções: exigir autenticação (ou um
perfil de administrador) para cadastrar usuários, ou criar o primeiro usuário só por seed. O
enunciado pede "autenticação JWT para APIs administrativas" e não detalha o cadastro; decidir e
documentar.

### 🟡 Chave de integração sem esquema de segurança no Swagger
`INTEGRACAO_API_KEY` já é repassada ao container pelo `docker-compose.yml`. No Swagger, a chave
aparece como parâmetro de cabeçalho, sem o cadeado de segurança; declarar um esquema `APIKeyHeader`
melhora a documentação (opcional).

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

### 🟡 Schemas ainda junto das rotas nos demais recursos
`ordens_servico.py` e `insumos.py` já têm requests/responses em `presentation/api/schemas/` e os
conversores de OS em `presentation/api/mappers/` (regra verificada por teste). `clientes.py`,
`servicos.py`, `veiculos.py`, `users.py`, `consulta_publica.py` e `integracoes.py` ainda mantêm os
schemas no mesmo arquivo das rotas; são arquivos pequenos (≤ 280 linhas), então é opcional.
`ordens_servico.py` continua com ~730 linhas de endpoints; dividi-lo em routers menores (ordens,
status, itens/insumos, execução) só vale se isso ainda incomodar.

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
  e usa valores de desenvolvimento para as credenciais (intencional, documentado no README).
- **Escalabilidade:** o vídeo precisa demonstrar a autoescala; `scripts/teste_fluxo_api.sh` pode
  servir de base para gerar múltiplas OS.
- **README:** hoje só tem uma linha de apresentação; faltam os objetivos de cada fase. Incluir
  arquitetura (componentes, infraestrutura, fluxo de deploy), execução local, deploy
  em Kubernetes, Terraform, link da collection de APIs e link do vídeo.
- **Documentação das APIs (collection):** hoje o README só cita o Swagger em
  `http://localhost:8000/docs`, que exige a aplicação rodando. Falta:
  - exportar o `openapi.json` (por script, a partir do próprio app) para `docs/`;
  - gerar a collection do Postman a partir dele;
  - uma seção "APIs" no README com os endpoints por grupo, o fluxo de autenticação (cadastro,
    login e token Bearer), as rotas públicas (`/consulta`) e as de integração externa
    (`/integracoes`, header `X-API-Key`), e os links para esses arquivos e para o `/docs`;

---

## Ordem sugerida

1. 🟡 Decidir o cadastro de usuários aberto.
2. Dockerfile → `/k8s` → `/infra` → CI/CD → README e vídeo.
