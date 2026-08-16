# Auditoria de Conformidade — api-oficina-mecanica × ENG-TECH-CHALLENGE.pdf

Revisão do que está **de fato implementado** no repositório contra as regras de negócio do
enunciado (Tech Challenge FIAP SOAT) — não do que está planejado. Cada item traz o veredito, a
evidência no código e, quando há lacuna, uma correção concreta.

- **Branch analisada:** `feature/pecas-e-insumos-os`
- **Testes:** 552 · **Cobertura:** 97%
- **Placar:** 18 conforme · 1 parcial · 1 lacuna · 1 crítico
- **Corrigidos desde a primeira rodada:** JWT nas APIs administrativas (crítico), orçamento gerado
  automaticamente (lacuna), consulta do cliente sem login administrativo (parcial) e peças/insumos
  avulsos na OS (lacuna) — todos marcados como ✅, com o achado original preservado para
  rastreabilidade.

> Legenda: ✅ Conforme · 🟡 Parcial · 🟠 Lacuna · 🔴 Crítico

---

## A. Criação da Ordem de Serviço

> "Identificação do cliente por CPF/CNPJ; cadastro do veículo; inclusão de serviços; possibilidade
> de incluir peças/insumos; orçamento gerado automaticamente; envio para aprovação."

### ✅ Identificação do cliente por CPF/CNPJ
O value object `CpfCnpj` normaliza a máscara e valida o dígito verificador de CPF (11) e CNPJ (14)
antes de aceitar o documento — rejeita sequências repetidas e checksums inválidos.

- `domain/value_objects/cpf_cnpj.py`

### ✅ Cadastro do veículo (placa, marca, modelo, ano)
Entidade `Veiculo` exige marca/cliente válidos, valida formato de placa (antiga e Mercosul) via VO
`Placa`, e limita o ano de fabricação a um intervalo plausível.

- `domain/entities/veiculo.py`
- `domain/value_objects/placa.py`

### ✅ Inclusão de serviços solicitados
`OrdemServico.adicionar_item` / `remover_item` impedem duplicidade, quantidade ≤ 0 e valor
negativo. Persistido em `ordem_servico_servicos`.

- `domain/entities/ordem_servico.py:42-71`

### ✅ Possibilidade de incluir peças e insumos na OS — Corrigido
> **Achado original (Lacuna):** não existia caminho para anexar um insumo diretamente a uma OS. O
> único vínculo era transitivo — a "receita" fixa de um serviço (`ServicoInsumoModel`), exibida
> como somente-leitura no detalhe da OS. Não havia coluna `insumo_id` em `ordem_servico_servicos`,
> nem endpoint, nem baixa de estoque associada a uma OS específica. Um mecânico não conseguia
> registrar "usei 2 unidades deste filtro nesta ordem" fora da receita pré-cadastrada do serviço.

Implementado exatamente como a sugestão original propunha: nova tabela de junção
`ordem_servico_insumos` (mesmo padrão de `ordem_servico_servicos`), métodos de domínio
`adicionar_insumo`/`remover_insumo` que espelham `adicionar_item`/`remover_item`, e dois novos
casos de uso — `AdicionarInsumoOrdemServicoUseCase` e `RemoverInsumoOrdemServicoUseCase` — que
chamam `InsumoRepository` para debitar/estornar o estoque, reaproveitando 100% a regra de
`Insumo.remover_estoque` (a mesma usada pelo CRUD de insumos, que já valida saldo insuficiente).

```python
# domain/entities/ordem_servico.py
def adicionar_insumo(self, insumo_id: str, valor: float, quantidade: int = 1):
    if not insumo_id:
        raise ValueError("ID do insumo é obrigatório")
    if quantidade <= 0:
        raise ValueError("Quantidade deve ser maior que zero")
    if valor < 0:
        raise ValueError("Valor não pode ser negativo")
    if any(item["insumo_id"] == insumo_id for item in self.insumos_utilizados):
        raise ValueError("Este insumo já foi adicionado à ordem de serviço")
    self.insumos_utilizados.append({...})
    self._atualizar_timestamp()

def remover_insumo(self, insumo_id: str) -> int:
    """Devolve a quantidade removida, para o caso de uso estornar o estoque."""
```

```python
# application/commands/adicionar_insumo_ordem_servico.py
async def execute(self, command):
    ordem_servico = await self.ordem_servico_repository.find_by_id(command.ordem_servico_id)
    if ordem_servico is None:
        return None

    insumo = await self.insumo_repository.find_by_id(command.insumo_id)
    if insumo is None:
        raise InsumoNaoEncontradoError(f"Insumo {command.insumo_id} não encontrado")

    insumo.remover_estoque(command.quantidade)  # valida saldo insuficiente
    ordem_servico.adicionar_insumo(
        insumo_id=str(command.insumo_id),
        valor=float(insumo.preco_unitario.value) if insumo.preco_unitario else 0.0,
        quantidade=command.quantidade,
    )

    await self.insumo_repository.update(insumo)
    return await self.ordem_servico_repository.save(ordem_servico)
```

Dois endpoints novos: `POST /ordens-servico/{id}/adicionar-insumo` e
`POST /ordens-servico/{id}/remover-insumo` — este último estorna a quantidade ao estoque, para que
remover um insumo por engano não deixe o saldo permanentemente a menos. `OrcamentoCalculado` (a
correção anterior) passou a somar também os insumos avulsos, então o orçamento automático já
reflete "serviços e peças", como o enunciado original pedia. O detalhe da OS
(`GET /ordens-servico/{id}`) ganhou um campo `insumos_utilizados`, distinto de
`itens[].insumos` (que continua mostrando a composição fixa de cada serviço).

**Ponto que ficou fora do escopo, por decisão consciente:** não há uma transação única cobrindo a
baixa de estoque e a persistência da OS — são dois commits sequenciais na mesma sessão. Se o
segundo falhar depois do primeiro ter sucesso, o estoque fica debitado sem o vínculo na OS
registrado. Nenhum outro fluxo do sistema usa transação explícita entre agregados (o próprio
`criar_ordem_servico.py` já opera assim), então mantive a mesma prática em vez de introduzir um
padrão novo isolado — mas é uma inconsistência real sob falha parcial, e vale endereçar se o time
decidir adotar `db.begin()` explícito de forma mais ampla.

**Arquivos:** `domain/entities/ordem_servico.py`, `infrastructure/database/models.py`,
`infrastructure/database/repositories/ordem_servico_repository_impl.py`,
`application/commands/adicionar_insumo_ordem_servico.py`,
`application/commands/remover_insumo_ordem_servico.py`,
`application/queries/get_ordem_servico_detalhada.py`,
`presentation/api/routes/ordens_servico.py`

### ✅ Orçamento gerado automaticamente a partir de serviços e peças — Corrigido
> **Achado original (Lacuna):** `orcamento` nunca era calculado — era sempre um número cru enviado
> pelo chamador da API, tanto na criação quanto em `enviar-aprovacao` (campo obrigatório no
> request). Nenhum dos pontos onde `orcamento` era atribuído somava
> `item["valor"] * item["quantidade"]`, contrariando o enunciado e permitindo que o cliente
> aprovasse um valor diferente do que a OS realmente continha.

A entidade passou a expor `orcamento_calculado`, que soma `valor × quantidade` de cada serviço da
OS (arredondado a 2 casas). `enviar_para_aprovacao` agora recebe `orcamento` **opcional**: quando
omitido, o valor é gerado automaticamente a partir dos itens; quando informado, prevalece — é o
que permite aplicar desconto ou acréscimo sobre o total.

```python
# domain/entities/ordem_servico.py
@property
def orcamento_calculado(self) -> float:
    total = sum(item["valor"] * item["quantidade"] for item in self.itens)
    return round(total, 2)

def enviar_para_aprovacao(self, orcamento: float = None, observacoes: str = None):
    self._validar_transicao(StatusOrdemServico.AGUARDANDO_APROVACAO)

    if orcamento is None:
        if not self.itens:
            raise ValueError(
                "Não é possível gerar o orçamento automaticamente: a ordem "
                "de serviço não possui serviços adicionados"
            )
        orcamento = self.orcamento_calculado

    self.orcamento = self._validar_orcamento(orcamento)
    ...
```

Junto com a correção principal, dois problemas adjacentes foram fechados:

- **Orçamento negativo aceito na criação.** `float(orcamento) if orcamento else None` aceitava
  `-500` sem reclamar, e `aprovar_e_iniciar_execucao` (`if not self.orcamento`) deixava passar,
  porque um negativo é *truthy*. Uma OS podia ser executada com orçamento negativo. Agora um
  `_validar_orcamento` compartilhado valida tanto o valor calculado quanto o manual, em ambos os
  caminhos.
- **Regra duplicada na camada de query.** `OrdemServicoDetalhada.valor_total_itens` reimplementava
  exatamente a mesma soma. Passou a delegar a `ordem_servico.orcamento_calculado` — a regra vive
  só no domínio.

O campo `orcamento` do request virou opcional e a resposta de `enviar-aprovacao` devolve o valor
orçado na mensagem, para o atendente conferir o que foi enviado ao cliente.

> **Sobre "e peças":** hoje as peças que um serviço consome já estão precificadas dentro do
> `valor` do próprio serviço (a receita em `ServicoInsumoModel`), então o total calculado as
> cobre. Peças avulsas, fora da receita, dependem da lacuna "incluir peças e insumos na OS" acima
> — quando ela for fechada, entram nessa mesma soma sem mudar a regra.

**Arquivos:** `domain/entities/ordem_servico.py`,
`application/commands/enviar_ordem_servico_para_aprovacao.py`,
`application/queries/get_ordem_servico_detalhada.py`,
`presentation/api/routes/ordens_servico.py`

**Ponto em aberto para o time decidir:** `adicionar_item` / `remover_item` não têm trava de status,
então os itens podem mudar depois que o orçamento já foi enviado, deixando `orcamento` (aprovado)
diferente de `orcamento_calculado` (atual). O detalhe da OS agora mostra os dois valores lado a
lado, mas não há bloqueio nem re-aprovação automática — vale definir se alterar itens após o envio
deve forçar a OS de volta para 'Em diagnóstico'.

### ✅ Envio do orçamento para aprovação do cliente
Use case dedicado (`EnviarOrdemServicoParaAprovacaoUseCase`) aplica a transição 'Em diagnóstico' →
'Aguardando aprovação' e persiste via o mesmo repositório usado no resto da aplicação.

- `application/commands/enviar_ordem_servico_para_aprovacao.py`

---

## B. Acompanhamento da Ordem de Serviço

> "6 status; atualização automática por ações do sistema; cliente consulta o andamento via API."

### ✅ Os 6 status, nomeados exatamente como no enunciado
`StatusOrdemServico` reproduz Recebida / Em diagnóstico / Aguardando aprovação / Em execução /
Finalizada / Entregue palavra por palavra, com um grafo de transições explícito que já impede
saltos inválidos (ex.: Recebida → Em execução direto).

- `domain/value_objects/status_ordem_servico.py`

### ✅ Atualização automática de status por ação do sistema
Cada transição tem um Command + UseCase dedicado (`iniciar_diagnostico_ordem_servico`,
`aprovar_orcamento_ordem_servico`, etc.), seguindo o mesmo padrão do resto do app — a rota apenas
monta o comando, o caso de uso decide e persiste.

- `application/commands/*_ordem_servico*.py`

### ✅ Cliente consulta o andamento via API — Corrigido
> **Achado original (Parcial):** o enunciado trata "cliente acompanha via app" e "APIs
> administrativas exigem JWT" como duas coisas separadas — sugerindo que a consulta do cliente não
> deveria depender do mesmo login administrativo. Só existia um caminho:
> `GET /ordens-servico/{id}`, protegido pelo `get_current_user` administrativo. Um cliente final
> não tinha como consultar sua própria OS sem uma conta de funcionário.

Novo endpoint `POST /consulta/ordens-servico`, sem token. A autorização vem da posse de dois dados
que só o dono reúne — o número da OS e o CPF/CNPJ cadastrado nela — e não de uma sessão de
funcionário. Aceita o documento com ou sem máscara.

Três decisões de projeto por trás disso:

- **Router e módulo próprios.** `ordens_servico.py` declara `Depends(get_current_user)` no nível do
  `APIRouter`, e o FastAPI não permite que um endpoint específico abra mão de uma dependência de
  router — uma rota pública ali seria impossível. A separação ainda deixa a fronteira de segurança
  explícita e dá ao endpoint uma tag própria no Swagger.
- **POST, não GET.** O CPF/CNPJ é dado pessoal: em query string acabaria em log de acesso,
  histórico do navegador e cabeçalho `Referer`. No corpo, não. Custa a semântica REST e vale a
  pena (LGPD).
- **404 idêntico para documento errado e OS inexistente.** Se as duas respostas diferissem, a rota
  viraria um oráculo para descobrir quais OS existem e a quem pertencem. Há teste garantindo que
  as respostas são idênticas.

A resposta é deliberadamente mais estreita que a administrativa: sem identificadores internos, sem
e-mail do cliente e sem `observacoes` — este último é texto livre preenchido por funcionários, que
podem não contar com ele sendo visível ao cliente. Traz status com descrição legível, serviços com
quantidade e valor, orçamento, total, veículo (placa/modelo) e um `aguardando_sua_aprovacao`.

**Arquivos:** `application/queries/consultar_ordem_servico_publica.py`,
`presentation/api/routes/consulta_publica.py`, `presentation/dependencies/dependencies.py`,
`main.py`

**Ponto de segurança em aberto:** não há *rate limiting*. Sabendo um número de OS, é possível
tentar documentos em força bruta. Na prática ~10⁹ CPFs válidos tornam isso inviável sem automação
pesada, mas um endpoint público sem limite é exposição real — fechar direito pede Redis ou
equivalente.

---

## C. Gestão administrativa

> "CRUD de clientes, veículos e serviços; CRUD (criar/ler/excluir) de peças com controle de
> estoque; listagem e detalhamento de OS; monitoramento do tempo médio de execução."

### ✅ CRUD de clientes, veículos e serviços
Os três seguem o mesmo desenho: entidade rica valida no construtor, Command/UseCase por operação,
repositório concreto por trás de uma interface ABC. Sem lacunas de negócio encontradas.

- `application/commands/{create,update,delete}_{cliente,veiculo,servico}.py`

### ✅ CRUD de peças/insumos com controle de estoque
O enunciado pede especificamente Create/Read/Delete — o repositório entrega isso e também Update,
o que é estritamente mais permissivo, não uma violação. Estoque tem entrada, saída (valida saldo
insuficiente) e ajuste absoluto, cada um com seu próprio caso de uso.

- `application/commands/{add,remove,adjust}_estoque.py`

### ✅ Listagem e detalhamento de OS
Listagem paginada com filtro por status, CPF/CNPJ do cliente e placa; detalhe agrega cliente,
veículo, itens e os insumos de cada serviço num único DTO.

- `application/queries/list_ordens_servico.py`
- `application/queries/get_ordem_servico_detalhada.py`

### 🟠 Monitoramento do tempo médio de execução do serviço — Lacuna
Não implementado. Não há endpoint, caso de uso ou query relacionada a tempo médio, KPI, dashboard
ou relatório em nenhuma das camadas. O único hit textual para "duração" é um campo livre e não
estruturado (`tempo_estimado`) na descrição de um *Serviço* do catálogo — não é medição real de
tempo de execução.

- `application/queries/` — nenhum resultado

**Sugestão de correção** — o histórico de status já grava timestamp de cada transição
(`HistoricoOrdemServicoModel.data_status`) — o material bruto para o cálculo já existe, só falta
agregá-lo. Query dedicada, na mesma pasta das demais:

```python
# application/queries/get_tempo_medio_execucao.py
class GetTempoMedioExecucaoUseCase:
    """Tempo médio entre 'Em execução' e 'Finalizada', nas OS já finalizadas."""

    def __init__(self, ordem_servico_repository: OrdemServicoRepository):
        self.ordem_servico_repository = ordem_servico_repository

    async def execute(self, periodo_dias: int = 30) -> TempoMedioExecucao:
        ordens = await self.ordem_servico_repository.find_finalizadas_desde(periodo_dias)
        duracoes = [o.duracao_execucao for o in ordens if o.duracao_execucao]
        return TempoMedioExecucao(
            media_horas=sum(duracoes) / len(duracoes) if duracoes else 0,
            amostra=len(duracoes),
        )
```

Expor como `GET /ordens-servico/metricas/tempo-medio-execucao`, protegido — é claramente um
endpoint administrativo, não um dado de cliente final.

---

## D. Segurança e qualidade

> "Autenticação JWT nas APIs administrativas; validação de CPF/CNPJ e placa; testes
> automatizados."

### ✅ JWT nas APIs administrativas — Corrigido
> **Achado original (Crítico):** `get_current_user` existia e funcionava, mas estava preso em só
> **2 de ~34 endpoints** (`GET /ordens-servico` e `GET /ordens-servico/{id}`). Todo o resto era
> acessível sem token: criar/editar/excluir clientes, veículos, serviços; criar/editar/excluir
> peças *e movimentar estoque*; criar uma OS; e as 8 transições de status (incluindo aprovar
> orçamento e entregar o veículo). Era o inverso do requisito — as leituras protegidas e as
> escritas administrativas, não.

A proteção passou para o nível do `APIRouter`, um único ponto de verdade por domínio, de modo que
um endpoint novo não nasce desprotegido por esquecimento:

```python
# presentation/api/routes/clientes.py (mesmo padrão em insumos, servicos, veiculos, ordens_servico)
router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    dependencies=[Depends(get_current_user)],  # aplica a TODAS as rotas abaixo
)
```

Verificado via schema OpenAPI: dos 34 endpoints, os únicos sem `security` são
`POST /users/register` e `POST /users/login` — públicos por definição, já que são o caminho para
obter o token. Os testes de integração ganharam um `unauthenticated_client` e um teste de 401 por
domínio, para que a regressão seja detectada e não apenas presumida.

**Arquivos:** `presentation/api/routes/{clientes,insumos,servicos,veiculos,ordens_servico}.py`,
`tests/integration/api/conftest.py`

### 🔴 Chave JWT: variável de ambiente inoperante — Crítico
`.env.example` declara `JWT_SECRET_KEY` / `JWT_ALGORITHM` / `JWT_EXPIRE_MINUTES`, mas `Settings`
(pydantic-settings) lê os nomes de campo `SECRET_KEY` / `ALGORITHM` /
`ACCESS_TOKEN_EXPIRE_MINUTES`, sem `env_prefix` nem `alias` ligando um ao outro. Resultado:
configurar `JWT_SECRET_KEY` no `.env` não tem efeito nenhum — em qualquer ambiente, inclusive
produção, a aplicação sempre cai no valor hardcoded no repositório
(`"42B38697D6C921058DDCFDD5ED5D89FAF0C671E3"`). Qualquer pessoa com acesso ao código-fonte
consegue forjar um JWT administrativo válido — achado direto para o "relatório de
vulnerabilidades" pedido no enunciado.

- `.env.example`
- `infrastructure/config/config.py:3-6`

**Sugestão de correção** — alinhar os nomes com `env_prefix` e remover o fallback hardcoded — se a
variável não estiver definida, a aplicação deve falhar ao subir, não usar um segredo público:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JWT_")

    SECRET_KEY: str  # obrigatório — lê JWT_SECRET_KEY, sem default
    ALGORITHM: str = "HS256"
    EXPIRE_MINUTES: int = 60

settings = Settings()
```

E renomear os usos de `settings.ACCESS_TOKEN_EXPIRE_MINUTES` para `settings.EXPIRE_MINUTES` em
`infrastructure/config/security.py`.

### ✅ Validação de CPF/CNPJ e placa
Ambos com dígito verificador real (não só formato) nos VOs `CpfCnpj` e `Placa`, reaproveitados em
toda entrada de cliente/veículo.

- `domain/value_objects/{cpf_cnpj,placa}.py`

### ✅ Testes unitários e de integração dos fluxos principais
485 testes, 97% de cobertura de linha+branch nos domínios críticos, separados em `tests/unit` e
`tests/integration` (repositórios contra SQLite real + API ponta a ponta via `TestClient`) — acima
do mínimo de 80% pedido.

- `tests/unit/`
- `tests/integration/`

---

## E. Requisitos técnicos

> "Monolito em camadas; Swagger; Dockerfile + docker-compose; README de configuração local."

### ✅ Monolito, arquitetura em camadas / DDD
`domain` → `application` → `infrastructure` → `presentation`, dependência sempre apontando para
dentro. Nenhuma camada externa vaza para o domínio.

### ✅ APIs REST documentadas via Swagger
Gerado automaticamente pelo FastAPI a partir dos `response_model` e docstrings de cada rota,
incluindo o esquema de segurança OAuth2 nos dois endpoints protegidos.

### ✅ Dockerfile + docker-compose.yml
Ambos presentes na raiz; README documenta `docker compose up --build`.

### 🟡 README com configuração local — Parcial
Cobre pré-requisitos, subida via Docker, logs, testes e cobertura. Não justifica explicitamente a
escolha do PostgreSQL — item pedido no enunciado ("a escolha do banco é livre, mas é necessário
justificá-la") e hoje ausente do texto. Correção é um parágrafo no README.

- `README.md`

---

## Conclusão

**Já corrigido nesta rodada:**

1. ✅ Superfície administrativa sem JWT — proteção movida para o nível do `APIRouter`; só
   `register` e `login` seguem públicos.
2. ✅ Orçamento automático — `orcamento_calculado` na entidade, com o valor manual virando
   override opcional para desconto/acréscimo.
3. ✅ Consulta do cliente — `POST /consulta/ordens-servico`, autenticado pela posse do número da
   OS + CPF/CNPJ, em router próprio e com resposta reduzida.
4. ✅ Peças/insumos avulsos na OS — nova tabela de junção, métodos de domínio espelhando os de
   serviço, e dois casos de uso que debitam/estornam o estoque via `Insumo.remover_estoque`.

**Aberto, em ordem de prioridade:**

1. 🔴 **Chave JWT hardcoded inoperante** — o único crítico restante e o de menor esforço:
   `JWT_SECRET_KEY` no `.env` não tem efeito nenhum, então a aplicação usa em qualquer ambiente o
   segredo versionado no repositório. Enquanto isso não for corrigido, qualquer pessoa com acesso
   ao código forja um token administrativo válido — e a proteção de JWT recém-adicionada não vale
   muito. Entra direto no relatório de vulnerabilidades pedido no enunciado.
2. 🟠 Tempo médio de execução (o histórico de status já tem os timestamps necessários).
3. 🟡 Justificativa da escolha do banco no README.
4. *Rate limiting* na consulta pública do cliente (ver seção B).
5. A baixa de estoque e a persistência da OS não são atômicas na adição de insumo (dois commits
   sequenciais) — ver nota na seção A.
