# Fase 2 — Plano de ação

Destilado de `docs/15SOAT - Fase 2 - Tech challenge.pdf` (enunciado original, PT-BR) em formato de
checklist acionável. A Fase 1 (CRUDs, DDD, JWT, orçamento, estoque) já está auditada em
`docs/auditoria-conformidade.md` — este documento cobre **apenas o que a Fase 2 acrescenta**:
qualidade/arquitetura do código e infraestrutura.

> Objetivo da fase: evoluir a aplicação da Fase 1 para suportar alta disponibilidade e picos de
> carga, com infraestrutura automatizada e código sustentável. Vale 60% da nota de todas as
> disciplinas da fase.

---

## 1. Código — refatoração

- [x] **Clean Code**: revisar nomes, simplicidade e coesão nos módulos existentes
      (`application/`, `domain/`, `infrastructure/`, `presentation/`).
      Feito: `presentation/api/routes/ordens_servico.py` (1333 → 1002 linhas) deixou de repetir
      `try/except` e o 404 em cada endpoint; passou a usar `presentation/api/error_handling.py`
      (`traduzir_erros`, `ordem_servico_ou_404`) e helpers de conversão de resposta.
- [x] **Clean Architecture / Arquitetura Hexagonal**: confirmar que as camadas já separadas
      (`domain` → `application` → `infrastructure`/`presentation`) não têm dependências invertidas
      (ex.: `domain` importando de `infrastructure`).
      Feito: `domain` não importa nada fora de si; `application` só importa `domain` e suas
      portas (`application/ports`: `PasswordHasher`, `TokenGenerator`; repositórios em
      `domain/repositories`). Os 3 use cases que usavam SQLAlchemy direto passaram a usar
      repositórios. `infrastructure` implementa as portas; `presentation` só toca
      `infrastructure` em `presentation/dependencies` (composição). A regra é garantida por
      `tests/unit/test_arquitetura.py`.
- [ ] **Testes automatizados**: já há suíte em `tests/` (573 testes, 97% cobertura por
      `auditoria-conformidade.md`) — validar que os fluxos críticos da Fase 2 (abaixo) também
      ficam cobertos.

## 2. APIs — alterar/criar

Verificar o que já existe em `presentation/api/routes/ordens_servico.py` e
`consulta_publica.py` antes de implementar — grande parte pode já estar coberta pela Fase 1.

- [ ] **Abertura de OS**: recebe cliente, veículo, serviços e peças; retorna ID único da OS.
- [ ] **Consulta de status da OS**: retorna um dos estados — `Recebida`, `Diagnóstico`,
      `Aguardando Aprovação`, `Execução`, `Finalizada`, `Entregue`.
- [ ] **Aprovação de orçamento**: endpoint para notificação externa de aprovação/recusa.
- [ ] **Listagem de ordens de serviço**:
  - [ ] Ordenar por status: `Execução > Aguardando Aprovação > Diagnóstico > Recebida`.
  - [ ] Dentro do mesmo status, mais antigas primeiro.
  - [ ] Excluir da listagem OS `Finalizada`/`Entregue` (exclusão **lógica**, não física).
- [ ] **Atualização de status da OS** via ferramenta externa (ex.: e-mail).

## 3. Infraestrutura

### Containerização
- [ ] `Dockerfile` atualizado (já existe na raiz — revisar).
- [ ] `docker-compose.yml` para desenvolvimento local (já existe — revisar).

### Kubernetes (`/k8s`)
- [ ] `Deployment`
- [ ] `Service`
- [ ] `ConfigMap` + `Secret` (variáveis sensíveis, ex. tokens de serviços externos)
- [ ] `HorizontalPodAutoscaler` (escala por CPU/memória)

### Infraestrutura como Código (`/infra`, Terraform)
- [ ] Provisionamento do cluster Kubernetes (local ou cloud)
- [ ] Provisionamento do banco de dados
- [ ] Documentação dos recursos criados e como aplicar (pode ir no README ou em `/infra/README.md`)

### CI/CD
- [ ] Pipeline (GitHub Actions, já que o repo está no GitHub) executando:
  - [ ] Build da aplicação
  - [ ] Testes automatizados
  - [ ] Build da imagem Docker
  - [ ] Deploy no cluster Kubernetes
  - [ ] Deploy do banco de dados
  - [ ] Aplicação dos manifestos YAML no cluster

## 4. Entregáveis finais

- [ ] Repositório com `/k8s`, `/infra`, pipeline CI/CD e código refatorado.
- [ ] `README.md` atualizado com:
  - [ ] Descrição da solução e objetivos da fase.
  - [ ] Desenho de arquitetura (componentes, infra provisionada, fluxo de deploy).
  - [ ] Instruções: execução local, deploy em Kubernetes, provisionamento via Terraform.
  - [ ] Link da collection de APIs (Postman/Swagger/similar).
  - [ ] Link de vídeo demonstrativo (YouTube/Vimeo, ≤15 min) mostrando: deploy, execução do
        CI/CD, consumo das APIs e escalabilidade automática (pode simular carga).
- [ ] Acesso do repositório compartilhado com o usuário GitHub `soat-architecture`.
- [ ] Entrega no portal do aluno: PDF com link do repo, desenho da arquitetura e link do vídeo.

---

## Observação

Os itens de código/API (seções 1–2) devem ser verificados contra o estado atual do repositório
antes de qualquer refatoração — é provável que parte já esteja implementada desde a Fase 1. As
seções 3–4 (infraestrutura, CI/CD, entregáveis) são, pelo histórico do repo, **trabalho novo**: não
há diretórios `/k8s` ou `/infra`, nem pipeline de CI/CD configurada até o momento.
