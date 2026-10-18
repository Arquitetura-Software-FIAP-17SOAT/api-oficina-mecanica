# Fase 1 — Plano de ação

Destilado de `docs/15SOAT - Fase 1 - Tech Challenge.pdf` (enunciado original, PT-BR) em formato de
checklist acionável. Este arquivo reúne **todo o conteúdo do enunciado** (contexto, proposta,
requisitos e entregáveis), de modo que o PDF possa ser removido do repositório sem perda de
informação. A maior parte do código já foi auditada contra este enunciado em
`docs/auditoria-conformidade.md` (22 conforme, 1 parcial, 1 lacuna, 1 crítico — todos os achados
corrigidos nas últimas rodadas). Este documento serve de referência rápida para prompts e não
substitui a auditoria detalhada.

> Objetivo da fase: MVP do back-end da oficina mecânica (gestão de OS, clientes, peças), com DDD
> e boas práticas de Qualidade de Software e Segurança. Vale 90% da nota da fase.

---

## 0. Enunciado — contexto e proposta

### Tech Challenge
O Tech Challenge é o projeto da fase e engloba os conhecimentos obtidos em todas as disciplinas
da fase. É uma atividade que, em princípio, deve ser desenvolvida **em grupo**. É **obrigatória** e
vale **90% da nota** da fase — atenção ao prazo de entrega. O time de professores fica disponível
no Discord para auxiliar durante todo o processo.

### Desafio
Uma oficina mecânica de médio porte, especializada em manutenção de veículos, tem enfrentado
desafios para expandir seus serviços com qualidade e eficiência. Hoje o processo de atendimento,
diagnóstico, execução de serviços e entrega dos veículos é desorganizado, feito com anotações
manuais e planilhas, o que gera estes problemas:

- Erros na priorização dos atendimentos;
- Falhas no controle de peças e insumos;
- Dificuldade em acompanhar o status dos serviços;
- Perda de histórico de clientes e veículos;
- Ineficiência no fluxo de orçamentos e autorizações.

Diante disso, a oficina decidiu investir em um **Sistema Integrado de Atendimento e Execução de
Serviços**, que permitirá aos clientes **acompanhar em tempo real** o andamento do serviço,
**autorizar reparos adicionais via aplicativo** e garantir uma gestão interna eficiente e segura.

### Proposta
Desenvolver a primeira versão (MVP) do back-end do sistema da oficina, com foco em **gestão de
ordens de serviço, clientes e peças**, aplicando **Domain-Driven Design (DDD)** e garantindo boas
práticas de **Qualidade de Software** e **Segurança**.

---

## 1. Fluxos principais

### Criação da Ordem de Serviço (OS)
- [x] Identificação do cliente por CPF/CNPJ.
      Verificado: `CpfCnpj` valida os dígitos; a consulta do cliente usa número da OS + CPF/CNPJ.
- [x] Cadastro de veículo (placa, marca, modelo, ano).
      Verificado: `POST /veiculos`, com `Placa` validada (formato antigo e Mercosul).
- [x] Inclusão dos serviços solicitados (ex.: troca de óleo, alinhamento).
- [x] Possibilidade de incluir peças e insumos necessários.
      Verificado: `adicionar-insumo`/`remover-insumo` e `insumos` na abertura da OS, com baixa de estoque.
- [x] Orçamento gerado automaticamente com base em serviços e peças.
      Verificado: `OrdemServico.orcamento_calculado` soma serviços e insumos; `enviar-aprovacao` sem valor usa o calculado.
- [x] Envio do orçamento ao cliente para aprovação.

### Acompanhamento da OS
- [x] Status: `Recebida`, `Em diagnóstico`, `Aguardando aprovação`, `Em execução`, `Finalizada`,
      `Entregue`.
- [x] Alteração automática dos status conforme ações no sistema.
      Verificado: um caso de uso por transição, com grafo de transições no `StatusOrdemServico`.
- [x] Consulta de progresso pelo cliente via API (o enunciado diz apenas "permitir consulta por
      parte do cliente via API para acompanhar o progresso"; a ausência de login administrativo é
      a interpretação adotada neste projeto).

### Gestão administrativa
- [x] CRUD de clientes.
- [x] CRUD de veículos.
- [x] CRUD de serviços.
- [x] CRUD de peças e insumos, com controle de estoque.
- [x] Listagem e detalhamento de ordens de serviço.
- [x] Monitoramento do tempo médio de execução dos serviços.
      Verificado: `GET /ordens-servico/metricas/tempo-medio-execucao`.

## 2. Segurança e qualidade

- [x] Autenticação JWT nas APIs administrativas.
      Verificado: 41 das 47 operações exigem JWT; as públicas são `register`, `login`, a consulta do
      cliente, `/health` e as de `/integracoes` (chave de API). Ressalvas na auditoria (seção 1): a
      chave JWT lida do ambiente e o cadastro de usuários aberto.
- [x] Validação de dados sensíveis (CPF/CNPJ, placa de veículo).
- [x] Testes unitários e de integração para os principais fluxos.
      Verificado: 698 testes, cobertura de 99% nos quatro pacotes.

## 3. Requisitos técnicos

- [x] Back-end monolítico. Por ser um MVP, é possível criar um monolito usando arquitetura em
      camadas.
- [x] Escolha do banco de dados é livre, mas **a preferência precisa ser justificada** (ver
      `README.md`, seção "Banco de dados" — já cobre PostgreSQL).
- [x] APIs RESTful documentadas via Swagger ou similar.
- [x] `Dockerfile` para build da aplicação. (Existe; o build não foi validado nesta revisão por falta de Docker.)
- [x] `docker-compose.yml` orquestrando o ambiente completo (API + PostgreSQL). Ver na auditoria o
      `INTEGRACAO_API_KEY` que o compose não repassa ao container.
- [x] Testes automatizados com cobertura mínima de 80% nos domínios críticos (99% medido).
- [x] Configuração para execução local simples (`README.md` explicativo).
      Atenção: o README afirma que `JWT_SECRET_KEY` é obrigatória e sem valor padrão, o que o código
      ainda não faz (ver auditoria, seção 1).
- [ ] Organização em repositório privado com acesso concedido ao usuário GitHub
      `soat-architecture`. (Não verificável pelo código: conferir nas configurações do GitHub.)

## 4. Entregáveis da Fase 1 (fora do código)

Itens conhecidos como **pendentes** pela última checagem (ver memória do projeto):

- [ ] Vídeo de até 15 minutos demonstrando todos os pontos do desafio (pode ser em grupo ou
      individual).
- [ ] Documentação DDD (Miro ou equivalente):
  - [ ] Event Storming completo dos fluxos: criação e acompanhamento da OS; gestão de peças e
        insumos.
  - [ ] Diagramas conforme apresentado na disciplina de DDD.
  - [ ] Linguagem Ubíqua aplicada.
- [ ] Relatório com análise de vulnerabilidades: incluir a análise do scan realizado no código.
- [ ] Documento de entrega (PDF) com:
  - [ ] Nome do grupo;
  - [ ] Participantes e usernames no Discord;
  - [ ] Link da documentação;
  - [ ] Link do repositório;
  - [ ] Relatório com análise de vulnerabilidades encontradas no sistema.
- [ ] Confirmação de que o repositório está compartilhado com `soat-architecture`.

## 5. Código-fonte (checklist de empacotamento)

- [x] APIs conforme os requisitos acima.
- [x] `Dockerfile` e `docker-compose.yml` configurados (funcionamento do build não validado nesta revisão).
- [ ] `README.md` completo com instruções de uso e objetivos.
      Faltam os objetivos da fase (hoje só uma linha de apresentação) e a seção de APIs.

---

## Observação

**Revisão de 2026-10-18:** itens das seções 1 a 3 e 5 conferidos contra o código, os testes
(698, 99% de cobertura) e o `openapi.json` (47 operações). Estão marcados os que foram verificados;
ficam em aberto o acesso do repositório a `soat-architecture` (configuração do GitHub), os
objetivos no README e a seção 4. Os pontos de atenção encontrados estão em
`docs/auditoria-conformidade.md`.

As seções 1–3 (fluxos, segurança, requisitos técnicos) estão **conformes**, com as ressalvas acima.
Qualquer prompt de melhoria deve primeiro checar a auditoria para não duplicar trabalho já
validado. A seção 4 (entregáveis fora do código: vídeo, documentação DDD em Miro, relatório de
vulnerabilidades, PDF de entrega) depende de artefatos externos ao repositório e não é verificável
por leitura de código — tratar como pendências de processo, não de implementação.
