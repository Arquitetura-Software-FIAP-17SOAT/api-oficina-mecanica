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
      (`application/`, `domain/`, `infrastructure/`, `presentation/`).
      Feito: `presentation/api/routes/ordens_servico.py` (1333 → 1002 linhas) deixou de repetir
      `try/except` e o 404 em cada endpoint; passou a usar `presentation/api/error_handling.py`
      (`traduzir_erros`, `ordem_servico_ou_404`) e helpers de conversão de resposta.
- [x] **Clean Architecture / Arquitetura Hexagonal** (separação adequada de camadas e
      dependências): confirmar que as camadas já separadas
      (`domain` → `application` → `infrastructure`/`presentation`) não têm dependências invertidas
      (ex.: `domain` importando de `infrastructure`).
      Feito: `domain` não importa nada fora de si; `application` só importa `domain` e suas
      portas (`application/ports`: `PasswordHasher`, `TokenGenerator`; repositórios em
      `domain/repositories`). Os 3 use cases que usavam SQLAlchemy direto passaram a usar
      repositórios. `infrastructure` implementa as portas; `presentation` só toca
      `infrastructure` em `presentation/dependencies` (composição). A regra é garantida por
      `tests/unit/test_arquitetura.py`.
- [x] **Testes automatizados**: já há suíte em `tests/` (614 testes, 99% de cobertura de
      `application/` + `presentation/`) — validar que os fluxos críticos da Fase 2 (abaixo) também
      ficam cobertos.
      Feito: fluxos já existentes (abertura de OS, consulta de status, aprovação/rejeição de
      orçamento, execução de serviço, consulta pública) estão cobertos por testes de API e de
      use case; lacunas fechadas em `finalizar_execucao_servico` e `error_handling`, e a regra de
      camadas tem teste próprio. **Pendente:** ordenação por status/antiguidade e exclusão lógica
      de `Finalizada`/`Entregue` na listagem (seção 2) ainda não existem — os testes devem ser
      escritos junto com essa implementação.

## 2. APIs — alterar/criar

Enunciado: refatorar o código da Fase 1 (seção 1) e alterar/criar as APIs abaixo.

Verificar o que já existe em `presentation/api/routes/ordens_servico.py` e
`consulta_publica.py` antes de implementar — grande parte pode já estar coberta pela Fase 1.

- [x] **Abertura de OS**: recebe os dados do cliente, veículo, serviços e peças; retorna a
      identificação única da OS.
      Feito: `POST /ordens-servico` aceita `cliente_id` (opcional, validado contra o dono do
      veículo), `servicos` e `insumos`; valida tudo antes de gravar (serviço/insumo inexistente ou
      estoque insuficiente não criam a OS nem baixam estoque) e retorna o `id`. Testes em
      `tests/integration/api/test_abertura_os_completa_api.py`.
      Limitação conhecida: a gravação da OS e a baixa de estoque são commits separados, então uma
      falha de banco entre os dois não é revertida — tratada como unidade de trabalho em
      `docs/auditoria-conformidade.md` (seção 3).
- [ ] **Consulta de status da OS**: informa a situação atual da OS, que é um dos estados — `Recebida`, `Diagnóstico`,
      `Aguardando Aprovação`, `Execução`, `Finalizada`, `Entregue`.
- [ ] **Aprovação de orçamento**: endpoint para receber notificações externas de aprovação ou
      recusa do orçamento do cliente.
- [ ] **Listagem de ordens de serviço**:
  - [ ] Ordenar por status: `Execução > Aguardando Aprovação > Diagnóstico > Recebida`.
  - [ ] Dentro do mesmo status, mais antigas primeiro.
  - [ ] Excluir da listagem OS `Finalizada`/`Entregue` (exclusão **lógica**, não física).
- [ ] **Atualização de status da OS** via alguma ferramenta como e-mail.

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
- [ ] `HorizontalPodAutoscaler` (escala por CPU/memória)

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
  - [ ] Descrição da solução e objetivos da fase.
  - [ ] Desenho da arquitetura proposta, incluindo: componentes da aplicação, infraestrutura
        provisionada e fluxo de deploy.
  - [ ] Instruções: execução local, deploy em Kubernetes, provisionamento via Terraform.
  - [ ] Link para a collection completa das APIs (Postman, Swagger ou similar).
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
