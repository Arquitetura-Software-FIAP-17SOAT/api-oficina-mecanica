#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
RESET_DB="${RESET_DB:-0}"

TMP_BODY="$(mktemp)"
trap 'rm -f "$TMP_BODY"' EXIT

TOKEN=""
AUTH_HEADER=()

ok()   { printf "\n✓ %s\n" "$1"; }
info() { printf "\n→ %s\n" "$1"; }
fail() {
  printf "\n✗ %s\n" "$1" >&2
  if [[ -s "$TMP_BODY" ]]; then
    echo "Resposta da API:" >&2
    cat "$TMP_BODY" | jq . 2>/dev/null || cat "$TMP_BODY" >&2
  fi
  exit 1
}

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Dependência ausente: $1"
    exit 1
  }
}

need curl
need jq
need python3

request() {
  local method="$1"
  local path="$2"
  local expected="$3"
  local body="${4:-}"

  local args=(-sS -o "$TMP_BODY" -w "%{http_code}" -X "$method" "${API_URL}${path}")

  if [[ ${#AUTH_HEADER[@]} -gt 0 ]]; then
    args+=(-H "${AUTH_HEADER[0]}")
  fi

  if [[ -n "$body" ]]; then
    args+=(-H "Content-Type: application/json" -d "$body")
  fi

  local code
  code="$(curl "${args[@]}")"

  if [[ "$code" != "$expected" ]]; then
    fail "$method $path retornou HTTP $code; esperado $expected"
  fi

  RESPONSE="$(cat "$TMP_BODY")"
}

assert_jq() {
  local expression="$1"
  local message="$2"

  if ! echo "$RESPONSE" | jq -e "$expression" >/dev/null 2>&1; then
    fail "$message"
  fi
}

generate_cpf() {
  python3 - <<'PY'
import secrets
while True:
    digits = [secrets.randbelow(10) for _ in range(9)]
    if len(set(digits)) == 1:
        continue
    s1 = sum(d * w for d, w in zip(digits, range(10, 1, -1)))
    d1 = (s1 * 10) % 11
    d1 = 0 if d1 == 10 else d1
    s2 = sum(d * w for d, w in zip(digits + [d1], range(11, 1, -1)))
    d2 = (s2 * 10) % 11
    d2 = 0 if d2 == 10 else d2
    print("".join(map(str, digits + [d1, d2])))
    break
PY
}

echo "========================================"
echo " TESTE API OFICINA MECÂNICA"
echo "========================================"
echo "API: $API_URL"

if [[ "$RESET_DB" == "1" ]]; then
  need docker
  info "Recriando banco local (ATENÇÃO: remove volumes do docker compose)"
  docker compose down -v
  docker compose up -d --build
fi

info "Aguardando API ficar disponível"
for _ in $(seq 1 60); do
  if curl -fsS "${API_URL}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! curl -fsS "${API_URL}/health" >/dev/null 2>&1; then
  echo "A API não respondeu em ${API_URL}/health"
  echo "Verifique: docker compose ps && docker compose logs -f api"
  exit 1
fi
ok "API disponível"

RUN_ID="$(date +%s)"
CPF="$(generate_cpf)"
LAST3="$(printf "%03d" $((10#$(date +%s) % 1000)))"
PLACA="TST${LAST3:0:1}A${LAST3:1:2}"
EMAIL="api.teste.${RUN_ID}@example.com"
PASSWORD="senha123"
USER_NAME="Usuário Teste ${RUN_ID}"
CLIENT_NAME="Cliente Teste ${RUN_ID}"
SERVICE_NAME="Troca de óleo teste ${RUN_ID}"
INPUT_NAME="Óleo 5W30 teste ${RUN_ID}"

info "1. Cadastrando usuário"
request POST "/users/register" 201 "$(jq -n --arg name "$USER_NAME" --arg email "$EMAIL" --arg password "$PASSWORD" '{name:$name,email:$email,password:$password}')"
USER_ID="$(echo "$RESPONSE" | jq -r '.user_id')"
[[ "$USER_ID" =~ ^[0-9]+$ ]] || fail "user_id não retornado corretamente"
ok "Usuário criado: USER_ID=$USER_ID"

info "2. Fazendo login"
request POST "/users/login" 200 "$(jq -n --arg email "$EMAIL" --arg password "$PASSWORD" '{email:$email,password:$password}')"
TOKEN="$(echo "$RESPONSE" | jq -r '.access_token')"
[[ -n "$TOKEN" && "$TOKEN" != "null" ]] || fail "access_token não retornado"
AUTH_HEADER=("Authorization: Bearer $TOKEN")
ok "Login realizado e token obtido"

info "3. Criando cliente com CPF válido"
request POST "/clientes" 201 "$(jq -n --arg nome "$CLIENT_NAME" --argjson usuario_id "$USER_ID" --arg cpf_cnpj "$CPF" --arg email "$EMAIL" '{nome:$nome,usuario_id:$usuario_id,cpf_cnpj:$cpf_cnpj,email:$email}')"
CLIENTE_ID="$(echo "$RESPONSE" | jq -r '.id')"
[[ "$CLIENTE_ID" =~ ^[0-9]+$ ]] || fail "cliente id não retornado"
ok "Cliente criado: CLIENTE_ID=$CLIENTE_ID | CPF=$CPF"

info "4. Criando veículo"
request POST "/veiculos" 201 "$(jq -n --argjson cliente_id "$CLIENTE_ID" --arg placa "$PLACA" '{cliente_id:$cliente_id,marca_id:1,placa:$placa,modelo:"Polo 1.0",ano_fabricacao:2024}')"
VEICULO_ID="$(echo "$RESPONSE" | jq -r '.id')"
[[ "$VEICULO_ID" =~ ^[0-9]+$ ]] || fail "veiculo id não retornado"
ok "Veículo criado: VEICULO_ID=$VEICULO_ID | PLACA=$PLACA"

info "5. Criando serviço"
request POST "/servicos" 201 "$(jq -n --arg nome "$SERVICE_NAME" '{nome:$nome,valor:"120.00",descricao:"Troca de óleo do motor",tempo_estimado:"1h"}')"
SERVICO_ID="$(echo "$RESPONSE" | jq -r '.id')"
[[ "$SERVICO_ID" =~ ^[0-9]+$ ]] || fail "servico id não retornado"
ok "Serviço criado: SERVICO_ID=$SERVICO_ID"

info "6. Criando insumo"
request POST "/insumos" 201 "$(jq -n --arg nome "$INPUT_NAME" '{nome:$nome,descricao:"Óleo sintético 5W30",preco_unitario:"50.00",estoque:10,quantidade_minima:3}')"
INSUMO_ID="$(echo "$RESPONSE" | jq -r '.id')"
[[ "$INSUMO_ID" =~ ^[0-9]+$ ]] || fail "insumo id não retornado"
ok "Insumo criado: INSUMO_ID=$INSUMO_ID | estoque=10"

info "7. Criando OS do fluxo aprovado"
request POST "/ordens-servico" 201 "$(jq -n --arg veiculo_id "$VEICULO_ID" '{veiculo_id:$veiculo_id,descricao:"Revisão e troca de óleo"}')"
ORDEM_ID="$(echo "$RESPONSE" | jq -r '.id')"
assert_jq '.status == "Recebida"' "OS deveria nascer em Recebida"
ok "OS criada: ORDEM_ID=$ORDEM_ID | status=Recebida"

info "8. Iniciando diagnóstico"
request POST "/ordens-servico/${ORDEM_ID}/iniciar-diagnostico" 200 '{"observacoes":"Veículo em diagnóstico"}'
assert_jq '.status == "Em diagnóstico"' "Status esperado: Em diagnóstico"
ok "Diagnóstico iniciado"

info "9. Adicionando serviço à OS"
request POST "/ordens-servico/${ORDEM_ID}/adicionar-item" 200 "$(jq -n --arg servico_id "$SERVICO_ID" '{servico_id:$servico_id,quantidade:1}')"
ok "Serviço adicionado à OS"

info "10. Adicionando 2 unidades de insumo avulso"
request POST "/ordens-servico/${ORDEM_ID}/adicionar-insumo" 200 "$(jq -n --argjson insumo_id "$INSUMO_ID" '{insumo_id:$insumo_id,quantidade:2}')"
ok "Insumo adicionado à OS"

info "11. Validando baixa automática do estoque (10 -> 8)"
request GET "/insumos/${INSUMO_ID}" 200
assert_jq '.estoque == 8' "Estoque deveria ser 8 após consumir 2 unidades"
ok "Estoque após consumo: 8"

info "12. Testando saída manual de estoque (8 -> 3)"
request POST "/insumos/${INSUMO_ID}/estoque/saida" 200 '{"quantidade":5}'
assert_jq '.estoque == 3' "Estoque deveria ser 3"
assert_jq '.estoque_baixo == true' "Insumo deveria estar com estoque baixo"
ok "Saída de estoque validada"

info "13. Validando listagem de estoque baixo"
request GET "/insumos/estoque-baixo" 200
if ! echo "$RESPONSE" | jq -e --argjson id "$INSUMO_ID" 'any(.[]; .id == $id)' >/dev/null; then
  fail "Insumo não apareceu em /insumos/estoque-baixo"
fi
ok "Insumo apareceu em estoque baixo"

info "14. Testando entrada manual de estoque (3 -> 5)"
request POST "/insumos/${INSUMO_ID}/estoque/entrada" 200 '{"quantidade":2}'
assert_jq '.estoque == 5' "Estoque deveria ser 5"
ok "Entrada de estoque validada"

info "15. Testando ajuste absoluto de estoque (5 -> 8)"
request POST "/insumos/${INSUMO_ID}/estoque/ajuste" 200 '{"quantidade":8}'
assert_jq '.estoque == 8' "Estoque deveria ser 8 após ajuste"
ok "Ajuste de estoque validado"

info "16. Enviando OS para aprovação com orçamento automático"
request POST "/ordens-servico/${ORDEM_ID}/enviar-aprovacao" 200 '{}'
assert_jq '.status == "Aguardando aprovação"' "Status esperado: Aguardando aprovação"
ok "OS enviada para aprovação"

info "17. Validando orçamento calculado e status do orçamento"
request GET "/ordens-servico/${ORDEM_ID}" 200
assert_jq '.status == "Aguardando aprovação"' "Status da OS incorreto"
assert_jq '.status_orcamento == "Pendente"' "status_orcamento deveria ser Pendente"
assert_jq '(.orcamento | tonumber) == 220' "Orçamento automático deveria ser 220.00"
ok "Orçamento automático validado: R$ 220,00"

info "18. Testando consulta pública do cliente sem autenticação"
SAVED_AUTH="${AUTH_HEADER[0]}"
AUTH_HEADER=()
request POST "/consulta/ordens-servico" 200 "$(jq -n --argjson numero_os "$ORDEM_ID" --arg cpf_cnpj "$CPF" '{numero_os:$numero_os,cpf_cnpj:$cpf_cnpj}')"
assert_jq '.numero_os == '"$ORDEM_ID" "Número da OS incorreto na consulta pública"
assert_jq '.aguardando_sua_aprovacao == true' "Consulta pública deveria indicar aguardando aprovação"
ok "Consulta pública validada"
AUTH_HEADER=("$SAVED_AUTH")

info "19. Aprovando orçamento e iniciando execução"
request POST "/ordens-servico/${ORDEM_ID}/aprovar-executar" 200
assert_jq '.status == "Em execução"' "Status esperado: Em execução"
ok "Orçamento aprovado e OS em execução"

info "20. Confirmando status_orcamento=Aprovado"
request GET "/ordens-servico/${ORDEM_ID}" 200
assert_jq '.status_orcamento == "Aprovado"' "status_orcamento deveria ser Aprovado"
ok "Status do orçamento validado"

info "21. Iniciando execução individual do serviço"
request POST "/ordens-servico/${ORDEM_ID}/servicos/${SERVICO_ID}/iniciar" 200 '{"data_inicio":"2025-01-15T10:00:00Z"}'
assert_jq '.data_inicio != null' "data_inicio deveria ter sido gravada"
ok "Execução do serviço iniciada"

info "22. Finalizando execução individual do serviço"
request POST "/ordens-servico/${ORDEM_ID}/servicos/${SERVICO_ID}/finalizar" 200 '{"data_fim":"2025-01-15T12:30:00Z"}'
assert_jq '(.tempo_execucao_horas | tonumber) == 2.5' "Tempo de execução deveria ser 2.5 horas"
ok "Execução concluída em 2.5 horas"

info "23. Validando métrica de tempo médio"
request GET "/ordens-servico/metricas/tempo-medio-execucao" 200
if ! echo "$RESPONSE" | jq -e --argjson sid "$SERVICO_ID" 'any(.[]; .servico_id == $sid and (.tempo_medio_horas | tonumber) == 2.5 and .quantidade_execucoes >= 1)' >/dev/null; then
  fail "Métrica esperada para o serviço não foi encontrada"
fi
ok "Métrica validada: média=2.5h"

info "24. Finalizando OS"
request POST "/ordens-servico/${ORDEM_ID}/finalizar" 200 '{"observacoes":"Serviço concluído com sucesso"}'
assert_jq '.status == "Finalizada"' "Status esperado: Finalizada"
ok "OS finalizada"

info "25. Entregando OS"
request POST "/ordens-servico/${ORDEM_ID}/entregar" 200 '{"observacoes":"Veículo entregue ao cliente"}'
assert_jq '.status == "Entregue"' "Status esperado: Entregue"
ok "OS entregue"

info "26. Criando segunda OS para fluxo rejeitado"
request POST "/ordens-servico" 201 "$(jq -n --arg veiculo_id "$VEICULO_ID" '{veiculo_id:$veiculo_id,descricao:"Diagnóstico para orçamento rejeitado"}')"
ORDEM_REJEITADA_ID="$(echo "$RESPONSE" | jq -r '.id')"
assert_jq '.status == "Recebida"' "Segunda OS deveria nascer em Recebida"
ok "Segunda OS criada: ORDEM_REJEITADA_ID=$ORDEM_REJEITADA_ID"

info "27. Iniciando diagnóstico da segunda OS"
request POST "/ordens-servico/${ORDEM_REJEITADA_ID}/iniciar-diagnostico" 200 '{}'
assert_jq '.status == "Em diagnóstico"' "Segunda OS deveria estar Em diagnóstico"
ok "Diagnóstico iniciado"

info "28. Adicionando serviço à segunda OS"
request POST "/ordens-servico/${ORDEM_REJEITADA_ID}/adicionar-item" 200 "$(jq -n --arg servico_id "$SERVICO_ID" '{servico_id:$servico_id,quantidade:1}')"
ok "Serviço adicionado"

info "29. Enviando segunda OS para aprovação"
request POST "/ordens-servico/${ORDEM_REJEITADA_ID}/enviar-aprovacao" 200 '{}'
assert_jq '.status == "Aguardando aprovação"' "Segunda OS deveria aguardar aprovação"
ok "Segunda OS aguardando aprovação"

info "30. Rejeitando orçamento"
request POST "/ordens-servico/${ORDEM_REJEITADA_ID}/rejeitar-orcamento" 200
assert_jq '.status == "Finalizada"' "Rejeição deveria finalizar a OS"
ok "Orçamento rejeitado e OS finalizada"

info "31. Confirmando status_orcamento=Rejeitado"
request GET "/ordens-servico/${ORDEM_REJEITADA_ID}" 200
assert_jq '.status == "Finalizada"' "Status final deveria ser Finalizada"
assert_jq '.status_orcamento == "Rejeitado"' "status_orcamento deveria ser Rejeitado"
ok "Fluxo de rejeição validado"

info "32. Validando listagem paginada de OS"
request GET "/ordens-servico?page=1&page_size=10" 200
assert_jq '.total >= 2' "Deveriam existir pelo menos duas OS"
ok "Listagem paginada validada"

info "33. Validando filtro por placa"
request GET "/ordens-servico?placa=${PLACA}&page=1&page_size=10" 200
if ! echo "$RESPONSE" | jq -e --argjson id "$ORDEM_ID" 'any(.itens[]; .id == $id)' >/dev/null; then
  fail "OS aprovada não foi encontrada pelo filtro de placa"
fi
ok "Filtro por placa validado"

echo
echo "========================================"
echo " TODOS OS TESTES PRINCIPAIS PASSARAM"
echo "========================================"
echo "USER_ID=$USER_ID"
echo "CLIENTE_ID=$CLIENTE_ID"
echo "VEICULO_ID=$VEICULO_ID"
echo "SERVICO_ID=$SERVICO_ID"
echo "INSUMO_ID=$INSUMO_ID"
echo "ORDEM_APROVADA_ID=$ORDEM_ID"
echo "ORDEM_REJEITADA_ID=$ORDEM_REJEITADA_ID"
echo "CPF_CLIENTE=$CPF"
echo "PLACA=$PLACA"
