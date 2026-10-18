# Fase 2 — Plano de ação

Destilado de `docs/15SOAT - Fase 2 - Tech challenge.pdf` (enunciado original, PT-BR) em formato de
checklist acionável. Este arquivo reúne **todo o conteúdo do enunciado** (problema, objetivo,
requisitos e entregáveis), de modo que o PDF possa ser removido do repositório sem perda de
informação. A Fase 1 (CRUDs, DDD, JWT, orçamento, estoque) já está auditada em
`docs/auditoria-conformidade.md` — este documento cobre **apenas o que a Fase 2 acrescenta**:
qualidade/arquitetura do código e infraestrutura.

> Objetivo da fase: evoluir a aplicação da Fase 1 para suportar alta disponibilidade e picos de
> carga, com infraestrutura automatizada e código sustentável. Vale 60% da nota de todas as
> disciplinas da fase.

---

## 0. Enunciado — problema e objetivo

### Tech Challenge
O Tech Challenge é o projeto da fase e engloba os conhecimentos obtidos em todas as disciplinas
da fase. É uma atividade que, em princípio, deve ser desenvolvida **em grupo**. É **obrigatória** e
vale **60% da nota de todas as disciplinas** da fase — atenção ao prazo de entrega.

### O problema
Após a implantação do sistema inicial para gestão de ordens de serviço, veículos, clientes e
controle de peças, a oficina mecânica conquistou maior eficiência no atendimento. Porém, com o
aumento da demanda, a expansão para novas unidades e a necessidade de garantir alta
disponibilidade do sistema, surgiu a necessidade de evoluir a aplicação. Agora, a oficina busca:

- Reduzir riscos operacionais por meio de infraestrutura escalável;
- Automatizar o provisionamento e o deploy do ambiente;
- Melhorar a qualidade e a organização do código, mantendo a evolução sustentável;
- Preparar a aplicação para suportar grandes volumes de ordens de serviço em horários de pico,
  com escalabilidade dinâmica.

### Objetivo
Evoluir a aplicação desenvolvida na Fase 1 para garantir **qualidade, resiliência e
escalabilidade**, incorporando práticas modernas de infraestrutura e automação.

---

## 1. Código — refatoração

- [x] **Clean Code** (nomes claros, simplicidade, coesão): revisar os módulos existentes
      (`application/`, `domain/`, `adapters/`, `presentation/`).
      Feito: erros e 404 das rotas centralizados em `presentation/api/error_handling.py`
      (`traduzir_erros`, `traduzir_value_error`, `encontrado_ou_404`, `exclusao_ou_404`); schemas e
      conversores de OS e insumos em `presentation/api/schemas/` e `presentation/api/mappers/`
      (`ordens_servico.py` foi de 1333 para 731 linhas, `insumos.py` de 437 para 251); seeders
      sem duplicação e scripts fora da raiz (`python -m adapters.database.seeders.executar`).
- [x] **Clean Architecture / Arquitetura Hexagonal** (separação adequada de camadas e
      dependências): confirmar que as camadas já separadas
      (`domain` → `application` → `adapters`/`presentation`) não têm dependências invertidas
      (ex.: `domain` importando de `adapters`).
      Feito: `domain` não importa nada fora de si; `application` só importa `domain` e as suas
      portas (`application/ports`: `PasswordHasher`, `TokenGenerator`, `TokenDecoder`,
      `UnitOfWork`; repositórios em `domain/repositories`). `adapters` (antes `infrastructure`)
      implementa as portas; `presentation` só toca `adapters` nos arquivos de composição de
      `presentation/dependencies`. A regra é garantida por `tests/unit/test_arquitetura.py`.
- [x] **Testes automatizados**: suíte em `tests/` com 698 testes e 99% de cobertura nos quatro
      pacotes — fluxos críticos da Fase 2 cobertos.
      Feito: abertura de OS (inclusive atomicidade com o estoque), consulta de status, aprovação e
      atualização de status por sistema externo, listagem ordenada com exclusão lógica, execução de
      serviço e consulta pública têm testes de API e de caso de uso; a regra de camadas e a de
      schemas fora das rotas têm teste próprio.

## 2. APIs — alterar/criar

Enunciado: refatorar o código da Fase 1 (seção 1) e alterar/criar as APIs abaixo.

Parte destes itens já estava coberta pela Fase 1; abaixo, o que foi feito em cada um.

- [x] **Abertura de OS**: recebe os dados do cliente, veículo, serviços e peças; retorna a
      identificação única da OS.
      Feito: `POST /ordens-servico` aceita `cliente_id` (opcional, validado contra o dono do
      veículo), `servicos` e `insumos`; valida tudo antes de gravar (serviço/insumo inexistente ou
      estoque insuficiente não criam a OS nem baixam estoque) e retorna o `id`. Testes em
      `tests/integration/api/test_abertura_os_completa_api.py`.
      A gravação da OS e a baixa de estoque são uma única transação (unidade de trabalho):
      falha em qualquer etapa desfaz tudo (`tests/integration/api/test_atomicidade_api.py`).
- [x] **Consulta de status da OS**: informa a situação atual da OS, que é um dos estados —
      `Recebida`, `Diagnóstico`, `Aguardando Aprovação`, `Execução`, `Finalizada`, `Entregue`.
      Feito (já coberto desde a Fase 1): `POST /consulta/ordens-servico` (cliente, sem login, por
      número da OS + CPF/CNPJ) devolve `status` e `status_descricao`; `GET /ordens-servico/{id}`
      (administrativo) devolve o `status` no detalhe. Teste que percorre os seis estados:
      `test_consulta_acompanha_os_por_todos_os_status`.
      Ponto de atenção: a API usa `Em diagnóstico` e `Em execução`; o enunciado da Fase 2 escreve
      `Diagnóstico` e `Execução`. São os mesmos estados, só muda a grafia — sem ação necessária.
- [x] **Aprovação de orçamento**: endpoint para receber notificações externas de aprovação ou
      recusa do orçamento do cliente.
      Feito: `POST /integracoes/ordens-servico/{id}/orcamento` com `{"decisao": "aprovado" |
      "recusado"}`, autenticado por chave de API no header `X-API-Key` (variável
      `INTEGRACAO_API_KEY`; sem ela a integração responde 503). Aprovado leva a OS a
      `Em execução`; recusado, a `Finalizada`. Reaproveita os use cases de aprovar/rejeitar.
      No Kubernetes, a chave entra como `Secret`. Testes em
      `tests/integration/api/test_integracoes_api.py`.
- [x] **Listagem de ordens de serviço**:
  - [x] Ordenar por status: `Execução > Aguardando Aprovação > Diagnóstico > Recebida`.
  - [x] Dentro do mesmo status, mais antigas primeiro.
  - [x] Excluir da listagem OS `Finalizada`/`Entregue` (exclusão **lógica**, não física).
        Feito: a regra vive no domínio (`PRIORIDADE_NA_LISTAGEM` e `STATUS_ENCERRADOS` em
        `status_ordem_servico.py`), o use case a repassa e o repositório a aplica (`CASE` no
        `ORDER BY` + `NOT IN`). As OS encerradas seguem no banco e consultáveis por
        `GET /ordens-servico/{id}`; filtrar `?status=Finalizada` ou `Entregue` devolve lista vazia.
        Testes em `tests/integration/api/test_listagem_ordens_servico_api.py`.
- [x] **Atualização de status da OS** via alguma ferramenta como e-mail.
      Feito: `POST /integracoes/ordens-servico/{id}/status` recebe a ação já interpretada pela
      ferramenta externa (por exemplo, um parser de e-mail), com `acao` entre `iniciar_diagnostico`,
      `enviar_para_aprovacao`, `retornar_para_diagnostico`, `finalizar` e `entregar`, e
      `observacoes` opcional (texto do e-mail). Mesma autenticação `X-API-Key` da aprovação de
      orçamento (que continua em `/orcamento`) e os mesmos use cases das rotas administrativas,
      então valem as mesmas regras de transição (ação inválida para o status atual: 400).
      O endpoint não lê e-mails nem integra com um provedor: quem faz isso chama a API.
      Testes em `tests/integration/api/test_integracoes_api.py`.

## 3. Infraestrutura

### Containerização
Garantir a aplicação containerizada via Docker.

- [ ] `Dockerfile` atualizado (já existe na raiz — revisar).
- [ ] `docker-compose.yml` para desenvolvimento local (já existe — revisar).

### Kubernetes (`/k8s`)
Criar manifestos YAML para deploy em Kubernetes, contemplando:

- [ ] `Deployment`
- [ ] `Service`
- [ ] `ConfigMap` + `Secret` (variáveis sensíveis, ex. tokens de serviços externos)
      Segredos da aplicação: `JWT_SECRET_KEY` (obrigatória, a aplicação não sobe sem ela) e
      `INTEGRACAO_API_KEY`. Podem reutilizar os valores de desenvolvimento do README.
- [ ] `HorizontalPodAutoscaler` (escala por CPU/memória)
- [ ] `Ingress` com limite de requisições (complementar ao enunciado): protege a consulta pública
      `POST /consulta/ordens-servico` contra força bruta de CPF/CNPJ. Anotações do `ingress-nginx`
      (`limit-rps` e `limit-connections`, por IP). Com várias réplicas sob HPA, o limite fica na
      borda e não no processo da aplicação; é preciso repassar o IP real (`X-Forwarded-For`).

### Infraestrutura como Código (`/infra`, Terraform)
Criar scripts em Terraform para:

- [ ] Provisionamento do cluster Kubernetes (local ou cloud)
- [ ] Provisionamento do banco de dados
- [ ] Documentação dos recursos criados e como aplicar (pode ir no README ou em `/infra/README.md`)

### CI/CD
Pipeline de CI/CD configurada (GitHub Actions, GitLab CI, etc.) que execute:

- [ ] Pipeline (GitHub Actions, já que o repo está no GitHub) executando:
  - [ ] Build da aplicação
  - [ ] Testes automatizados
  - [ ] Build da imagem Docker
  - [ ] Deploy no cluster Kubernetes
  - [ ] Deploy do banco de dados
  - [ ] Aplicação dos manifestos YAML no cluster

## 4. Entregáveis finais

- [ ] Repositório git (o mesmo da Fase 1) com o código-fonte atualizado e refatorado seguindo as
      boas práticas da arquitetura escolhida, contendo: `Dockerfile` e `docker-compose` revisados,
      manifestos Kubernetes em `/k8s`, scripts Terraform em `/infra` e arquivos de configuração da
      pipeline CI/CD.
- [ ] `README.md` atualizado com:
  - [x] Descrição da solução e objetivos da fase (README: "Objetivos das fases" e "Estado da
        Fase 2").
  - [ ] Desenho da arquitetura proposta, incluindo: componentes da aplicação, infraestrutura
        provisionada e fluxo de deploy. (Componentes da aplicação: README, "Arquitetura"; faltam a
        infraestrutura provisionada e o fluxo de deploy.)
  - [ ] Instruções: execução local, deploy em Kubernetes, provisionamento via Terraform.
        (Execução local: feita; Kubernetes e Terraform: pendentes.)
  - [ ] Link para a collection completa das APIs (Postman, Swagger ou similar). (O README já traz a
        tabela de rotas e o link local do Swagger; falta o `openapi.json` exportado e a collection.)
  - [ ] Link para vídeo demonstrativo do ambiente em execução, publicado no YouTube ou Vimeo
        (público ou não listado), de até 15 minutos. Deve demonstrar: deploy da aplicação,
        execução do CI/CD, consumo das APIs e escalabilidade automática (pode simular aumento de
        carga ou múltiplas ordens de serviço).
- [ ] Acesso do repositório compartilhado com o usuário GitHub `soat-architecture`.
- [ ] Entrega no portal do aluno: PDF contendo o link do repositório GitHub compartilhado com o
      usuário `soat-architecture`, o desenho da arquitetura com os recursos escolhidos e o link do
      vídeo (até 15 minutos) apresentando a solução desenvolvida.

---

## Observação

Os itens de código/API (seções 1–2) devem ser verificados contra o estado atual do repositório
antes de qualquer refatoração — é provável que parte já esteja implementada desde a Fase 1. As
seções 3–4 (infraestrutura, CI/CD, entregáveis) são, pelo histórico do repo, **trabalho novo**: não
há diretórios `/k8s` ou `/infra`, nem pipeline de CI/CD configurada até o momento.
