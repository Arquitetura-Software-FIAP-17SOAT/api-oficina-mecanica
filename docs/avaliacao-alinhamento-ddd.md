# Avaliação de Alinhamento — Enunciado × Event Storming × Código

Cruzamento de três fontes para a entrega da Fase 1 (Tech Challenge FIAP SOAT):

1. **Enunciado oficial** — `15SOAT - Fase 1 - Tech Challenge.pdf` + imagem complementar
   ("Para deixar o requisito mais objetivo, na Fase 1 esperamos, no mínimo, os seguintes artefatos");
2. **Event Storming** — board do Miro (`uXjVH6ubcUI=`), analisado pelo export
   `Arquitetura-Software-Post-Tech-Challenge.pdf`;
3. **Código** — branch `main` (commit `4a0a1a1`).

O enunciado é o **árbitro**: quando board e código discordam, prevalece o que o enunciado pede.

- **Data da avaliação:** 2026-08-29
- **Complementa:** `docs/auditoria-conformidade.md` (cruzamento enunciado × código já feito lá;
  este documento foca no board e no alinhamento entre as três pontas)

> Legenda: ✅ Alinhado · 🟡 Parcial · ❌ Desalinhado · 🔍 Pendente de verificação

## Limitação de leitura do board

O export do Miro é **raster de ~1164px para o board inteiro** — sem texto extraível. A leitura foi
feita por recorte e ampliação região a região. Saíram legíveis: catálogos de Eventos, Comandos,
Atores e Agregados da seção **Acompanhamento de OS**. Ficaram **abaixo do limite de resolução**
(tudo o que estiver marcado 🔍 depende de novos prints com zoom):

- Seção **Gestão de Peças e Insumos** (leitura apenas provável);
- **Políticas** (3 post-its roxos), **Modelos de Leitura** (6 verdes, semi-legíveis),
  **Sistemas Externos** (rosas), **Pontos de Atenção** (losangos vermelhos).

---

## 1. Estrutura do entregável Event Storming — ✅

O enunciado exige Event Storming de exatamente **2 fluxos**: "Criação e acompanhamento da OS" e
"Gestão de peças e insumos". O board tem exatamente essas duas seções. Os sub-fluxos da imagem
complementar (elaboração/aprovação/reprovação do orçamento; execução e finalização do serviço)
estão contemplados dentro de "Acompanhamento de OS". **Estruturalmente o board cobre o pedido.**

Inventário lido da seção Acompanhamento de OS:

- **Atores (3):** Recepcionista · Cliente · Mecânico
- **Agregados (7):** Cliente · Veículo · Ordem de Serviço (OS) · Diagnóstico · Orçamento ·
  Execução · Entrega
- **Eventos (16)** e **Comandos (16)** — cruzados nas seções seguintes.

## 2. Criação da OS — os 6 bullets obrigatórios

| Requisito do enunciado | Board | Código | Situação |
|---|---|---|---|
| Identificação do cliente por CPF/CNPJ | Cadastro de Cliente e Veículo Iniciado | VO `CpfCnpj` com dígito verificador | ✅ |
| Cadastro de veículo (placa, marca, modelo, ano) | Cadastrar Veículo e Cliente | `Veiculo` + VO `Placa` | ✅ |
| Inclusão dos serviços solicitados | Peças e Serviços adicionados à OS | `OrdemServico.adicionar_item` | ✅ |
| Incluir peças e insumos | mesmo evento + seção própria | `adicionar_insumo` + baixa de estoque | ✅ |
| Orçamento gerado automaticamente | Calcular Orçamento → Orçamento Calculado | `orcamento_calculado` quando não informado manual | ✅ |
| Envio do orçamento ao cliente para aprovação | Enviar Orçamento ao Cliente | só transição para `AGUARDANDO_APROVACAO` — não há envio/notificação | 🟡 código |

## 3. Acompanhamento da OS — os 6 status batem 1:1

| Status (enunciado) | Evento no board | Código |
|---|---|---|
| Recebida | Ordem de Serviço Criada | ✅ `RECEBIDA` |
| Em diagnóstico | Diagnóstico Iniciado | ✅ `EM_DIAGNOSTICO` |
| Aguardando aprovação | Orçamento Enviado ao Cliente | ✅ `AGUARDANDO_APROVACAO` |
| Em execução | Orçamento Aprovado | ✅ `EM_EXECUCAO` |
| Finalizada | Ordem de Serviço Finalizada | ✅ `FINALIZADA` |
| Entregue | Veículo Entregue | ✅ `ENTREGUE` |

Também alinhados nas três pontas:

- **Reprovação do orçamento** (imagem complementar): board `Orçamento Rejeitado` · código
  `rejeitar_orcamento()` → `FINALIZADA` — ✅;
- **Alteração automática de status conforme ações**: transições embutidas nas ações de domínio
  (`StatusOrdemServico.get_transicoes_validas`) — ✅;
- **Consulta pelo cliente via API**: código ✅ (nº da OS + CPF/CNPJ, sem login administrativo);
  board 🔍 (Modelos de Leitura semi-legíveis sugerem "Status da OS", "Orçamento da OS");
- **Tempo médio de execução**: eventos `Execução de Serviço Iniciada/Concluída` no board são
  exatamente o que alimenta `list_tempo_medio_execucao` no código — ✅.

## 4. Elementos órfãos do board — arbitragem pelo enunciado

| Elemento do board | Veredito | Ação recomendada |
|---|---|---|
| **Ordem de Serviço Iniciada** (evento) | ❌ Não existe status "Iniciada" nos 6 do enunciado nem transição no código. **O código está certo; o board tem um evento a mais** | Remover do board, ou anotar como marco interno sem mudança de status |
| **Atendimento Finalizado** (evento) | ❌ Nenhum status corresponde; órfão no enunciado e no código | Remover, ou virar nota pós-Entregue |
| **Notificar cliente** (post-it amarelo = evento, mas descreve ação) | 🟡 Aqui **o board está certo e o código deve**: "envio do orçamento ao cliente" é bullet obrigatório do enunciado. Há ainda o erro de cor (ação pintada como evento) | Recolorir como comando/política no board; no código, registrar o envio (ou documentar notificação como fora do MVP num Ponto de Atenção) |
| **Notificar de Retirada do Veículo** (comando) | 🟡 Sem contraparte no código | Mesma decisão do item acima |

## 5. Gestão de peças e insumos — 🔍 leitura provável

A seção existe (exigência formal atendida), mas o texto está no limite da resolução. Leitura
**provável** dos eventos: item selecionado/reservado para a OS · item indisponível identificado ·
compra do item solicitada · item comprado · item recebido · estoque atualizado · item utilizado
na OS · item disponibilizado.

Se essa leitura se confirmar, há **duas divergências board × código**:

1. **Reserva de item** — o código debita o estoque imediatamente
   (`Insumo.remover_estoque` chamado por `AdicionarInsumoOrdemServicoUseCase`); não existe
   conceito de reserva;
2. **Fluxo de compra/reposição** — o código tem apenas `AddEstoqueUseCase` genérico; não existem
   "solicitar compra" nem "registrar recebimento".

**Pendência:** prints com zoom desta seção + Políticas + Sistemas Externos + Pontos de Atenção
para fechar a matriz.

## 6. Linguagem Ubíqua — colisões (o enunciado exige "aplicada")

| Termo | No board | No código | Problema |
|---|---|---|---|
| **Peça / Item / Insumo** | seção de peças chama a peça de "Item" | `itens` da OS = **serviços**; peça = `insumo` | Mesma palavra, três significados. Colisão direta que o glossário (inexistente) deveria impedir |
| **Agregados** (raias) | Diagnóstico, Orçamento, Execução, Entrega rotulados como agregados | são status/campos dentro de `OrdemServico` | Diagrama de domínio vai contradizer o board (ver §7) |
| **Atores** | Recepcionista, Cliente, Mecânico | `Usuario` sem papel; JWT sem role; nenhuma rota checa permissão | Qualquer usuário logado faz tudo |
| **Diagnóstico Concluído** | evento próprio + comando Concluir Diagnóstico | fundido com o envio em `enviar_para_aprovacao()` | Um passo do board = meio passo do código |
| **Atendimento** | "Atendimento Finalizado" | conceito não existe | Termo sem definição |
| **Usuário** (fora do board) | — | `Usuario`/`name`/`hashed_password` · tabela `usuarios`/`nome`/`senha_hash` · `UserRepository`/`register_user` | Três idiomas para o mesmo conceito |

## 7. Agregados — board (7) × código (5)

Agregados reais no código: **Cliente, Veículo, Ordem de Serviço, Serviço, Insumo** (+ `Usuario`
para autenticação). Diagnóstico, Orçamento, Execução e Entrega **não** têm identidade, ciclo de
vida nem repositório — são fases/status da OS. As mesmas 7 palavras aparecem como **raias** na
versão linear do board, confirmando o uso como fases do fluxo.

Correção mais barata: renomear no board o rótulo "Agregados" das raias para "Fases" e manter no
catálogo de agregados apenas Cliente, Veículo e OS (+ Serviço e Insumo, que o board de OS não
cita). A alternativa — reificar Diagnóstico/Orçamento/Execução/Entrega como agregados no código —
é reescrita grande, sem exigência do enunciado.

## 8. Divergências código × board já conhecidas (resumo)

Registradas em detalhe em `docs/auditoria-conformidade.md` e na rodada de auditoria; entram aqui
como placar:

- **Zero eventos de domínio no código** — os 16 eventos do board são todos inferidos de mutação
  de status; não há classes de evento nem publicação;
- **`motivo` da transição descartado na persistência** — o domínio registra
  `{status, data, motivo}`, mas `historico_ordem_servico` não tem coluna de motivo e a releitura
  injeta o literal "Histórico recuperado do banco"
  (`infrastructure/database/repositories/ordem_servico_repository_impl.py`);
- **Execução de serviço fora do domínio** — `iniciar/finalizar_execucao_servico.py` usam
  SQLAlchemy direto na camada de aplicação, com as regras (data futura, `data_fim ≥ data_inicio`)
  fora da entidade;
- **Sem transação entre OS e estoque** — falha parcial pode debitar estoque sem registrar o
  vínculo na OS (decisão consciente, documentada na auditoria).

## 9. Checklist de artefatos exigidos na Fase 1

| Artefato | Status |
|---|---|
| Event Storming — Criação e acompanhamento da OS | ✅ no board |
| Event Storming — Gestão de peças e insumos | ✅ presente · 🔍 conteúdo a confirmar |
| Event Storming — orçamento (elaboração/aprovação/reprovação) | ✅ dentro de Acompanhamento |
| Event Storming — execução e finalização | ✅ dentro de Acompanhamento |
| **Context Map / Bounded Contexts** | ❌ não encontrado no export |
| **Diagrama do modelo de domínio** (agregados, entidades, VOs, eventos, regras) | ❌ não encontrado no export |
| **Linguagem Ubíqua** (glossário) | ❌ não encontrado no export |
| Código: APIs, Docker, testes ≥80%, JWT, Swagger, README | ✅ ver `docs/auditoria-conformidade.md` |
| Vídeo (≤15 min) · Relatório de vulnerabilidades · PDF de entrega | fora do escopo desta avaliação |

Se Context Map, diagrama de domínio e glossário existirem em outro frame do Miro não coberto pelo
export, atualizar esta tabela; caso contrário, são **entregáveis em aberto**.

## 10. Plano de correção recomendado

**No Miro (~15 min):**

1. Remover (ou anotar como marco interno) os eventos "Ordem de Serviço Iniciada" e
   "Atendimento Finalizado";
2. Recolorir "Notificar cliente" de evento para comando/política;
3. Renomear rótulo das raias de "Agregados" para "Fases";
4. Padronizar "Item" → "Peça/Insumo" na seção de peças (ou declarar sinônimos no glossário).

**Decisões de grupo:**

5. Notificação (envio de orçamento + retirada do veículo): implementar registro de envio no
   código **ou** documentar como fora do MVP num Ponto de Atenção do board;
6. Reserva e compra de item (se confirmadas no board): implementar, simplificar o board, ou
   marcar como fase futura.

**Artefatos a produzir:**

7. Context Map / Bounded Contexts;
8. Diagrama do modelo de domínio;
9. Glossário de Linguagem Ubíqua (resolvendo as colisões da §6).

**No código (menor prioridade para a nota, maior para a consistência):**

10. Persistir o `motivo` do histórico de status;
11. Trazer início/fim de execução de serviço para dentro do domínio;
12. Papéis/roles nos usuários, se o grupo quiser refletir os 3 atores do board.

## Conclusão

- **Board × enunciado: forte.** Os 2 fluxos exigidos, os 6 status e a reprovação do orçamento
  estão no board; os desvios são 2 eventos órfãos e 1 post-it com a cor errada.
- **Código × enunciado: forte** (placar detalhado na auditoria: 22 conforme).
- **Board × código: é onde mora o desalinhamento.** Notificação modelada e inexistente,
  Peça/Item/Insumo trocados, raias rotuladas de agregados, possivelmente reserva/compra de
  estoque — mais os três artefatos DDD ausentes (Context Map, diagrama de domínio, glossário).

A correção estrutural mais barata está no board e no glossário, não no código.
