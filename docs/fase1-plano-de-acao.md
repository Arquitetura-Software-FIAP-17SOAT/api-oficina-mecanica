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
- [ ] Identificação do cliente por CPF/CNPJ.
- [ ] Cadastro de veículo (placa, marca, modelo, ano).
- [ ] Inclusão dos serviços solicitados (ex.: troca de óleo, alinhamento).
- [ ] Possibilidade de incluir peças e insumos necessários.
- [ ] Orçamento gerado automaticamente com base em serviços e peças.
- [ ] Envio do orçamento ao cliente para aprovação.

### Acompanhamento da OS
- [ ] Status: `Recebida`, `Em diagnóstico`, `Aguardando aprovação`, `Em execução`, `Finalizada`,
      `Entregue`.
- [ ] Alteração automática dos status conforme ações no sistema.
- [ ] Consulta de progresso pelo cliente via API (o enunciado diz apenas "permitir consulta por
      parte do cliente via API para acompanhar o progresso"; a ausência de login administrativo é
      a interpretação adotada neste projeto).

### Gestão administrativa
- [ ] CRUD de clientes.
- [ ] CRUD de veículos.
- [ ] CRUD de serviços.
- [ ] CRUD de peças e insumos, com controle de estoque.
- [ ] Listagem e detalhamento de ordens de serviço.
- [ ] Monitoramento do tempo médio de execução dos serviços.

## 2. Segurança e qualidade

- [ ] Autenticação JWT nas APIs administrativas.
- [ ] Validação de dados sensíveis (CPF/CNPJ, placa de veículo).
- [ ] Testes unitários e de integração para os principais fluxos.

## 3. Requisitos técnicos

- [ ] Back-end monolítico. Por ser um MVP, é possível criar um monolito usando arquitetura em
      camadas.
- [ ] Escolha do banco de dados é livre, mas **a preferência precisa ser justificada** (ver
      `README.md`, seção "Banco de dados" — já cobre PostgreSQL).
- [ ] APIs RESTful documentadas via Swagger ou similar.
- [ ] `Dockerfile` para build da aplicação.
- [ ] `docker-compose.yml` orquestrando o ambiente completo.
- [ ] Testes automatizados com cobertura mínima de 80% nos domínios críticos.
- [ ] Configuração para execução local simples (`README.md` explicativo).
- [ ] Organização em repositório privado com acesso concedido ao usuário GitHub
      `soat-architecture`.

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

- [ ] APIs conforme os requisitos acima.
- [ ] `Dockerfile` e `docker-compose.yml` configurados e funcionais.
- [ ] `README.md` completo com instruções de uso e objetivos.

---

## Observação

As seções 1–3 (fluxos, segurança, requisitos técnicos) são, pela auditoria mais recente
(`docs/auditoria-conformidade.md`), **essencialmente conformes** — qualquer prompt de melhoria
deve primeiro checar esse documento para não duplicar trabalho já validado. A seção 4
(entregáveis fora do código: vídeo, documentação DDD em Miro, relatório de vulnerabilidades,
PDF de entrega) depende de artefatos externos ao repositório e não é verificável por leitura de
código — tratar como pendências de processo, não de implementação.
