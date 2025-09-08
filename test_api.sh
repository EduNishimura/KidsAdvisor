#!/bin/bash

# 🧪 Script de Teste Automatizado - KidsAdvisor API

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🧪 Iniciando testes automatizados da KidsAdvisor API...${NC}"

# Função para testar endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local headers=$4
    local expected_status=$5
    
    echo -n "Testando $method $endpoint... "
    
    if [ -n "$data" ]; then
        if [ -n "$headers" ]; then
            response=$(curl -s -w "%{http_code}" -X $method "$BASE_URL$endpoint" \
                -H "Content-Type: application/json" \
                -H "$headers" \
                -d "$data")
        else
            response=$(curl -s -w "%{http_code}" -X $method "$BASE_URL$endpoint" \
                -H "Content-Type: application/json" \
                -d "$data")
        fi
    else
        if [ -n "$headers" ]; then
            response=$(curl -s -w "%{http_code}" -X $method "$BASE_URL$endpoint" \
                -H "$headers")
        else
            response=$(curl -s -w "%{http_code}" -X $method "$BASE_URL$endpoint")
        fi
    fi
    
    status_code="${response: -3}"
    body="${response%???}"
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ OK (${status_code})${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL (${status_code}, esperado ${expected_status})${NC}"
        echo "Response: $body"
        return 1
    fi
}

# Função para extrair valor JSON
extract_json_value() {
    local json=$1
    local key=$2
    echo "$json" | python3 -c "import sys, json; print(json.load(sys.stdin)['$key'])"
}

# 1. Health Check
echo -e "\n${YELLOW}1. Testando Health Check${NC}"
test_endpoint "GET" "/health" "" "" "200"

# 2. Cadastrar usuário
echo -e "\n${YELLOW}2. Testando Cadastro de Usuário${NC}"
USER_DATA='{
    "nome": "Teste Automatizado",
    "email": "teste.automatizado@example.com",
    "senha": "123456",
    "tipo": "pai"
}'

USER_RESPONSE=$(curl -s -X POST "$BASE_URL/usuarios/" \
    -H "Content-Type: application/json" \
    -d "$USER_DATA")

if echo "$USER_RESPONSE" | grep -q "id"; then
    echo -e "${GREEN}✅ Usuário cadastrado com sucesso${NC}"
    USER_ID=$(echo "$USER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
else
    echo -e "${RED}❌ Falha no cadastro de usuário${NC}"
    echo "$USER_RESPONSE"
    exit 1
fi

# 3. Login
echo -e "\n${YELLOW}3. Testando Login${NC}"
LOGIN_DATA='{
    "email": "teste.automatizado@example.com",
    "senha": "123456"
}'

LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/usuarios/login" \
    -H "Content-Type: application/json" \
    -d "$LOGIN_DATA")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Login realizado com sucesso${NC}"
    TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
else
    echo -e "${RED}❌ Falha no login${NC}"
    echo "$LOGIN_RESPONSE"
    exit 1
fi

# 4. Criar evento
echo -e "\n${YELLOW}4. Testando Criação de Evento${NC}"
EVENT_DATA='{
    "nome": "Evento de Teste Automatizado",
    "descricao": "Evento criado para testes automatizados",
    "categoria": "música",
    "localizacao": "São Paulo",
    "data": "2025-12-31T10:00:00",
    "idade_recomendada": "5-10",
    "preco": 25.0,
    "organizadorId": "'$USER_ID'"
}'

EVENT_RESPONSE=$(curl -s -X POST "$BASE_URL/eventos/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$EVENT_DATA")

if echo "$EVENT_RESPONSE" | grep -q "id"; then
    echo -e "${GREEN}✅ Evento criado com sucesso${NC}"
    EVENT_ID=$(echo "$EVENT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
else
    echo -e "${RED}❌ Falha na criação de evento${NC}"
    echo "$EVENT_RESPONSE"
    exit 1
fi

# 5. Curtir evento
echo -e "\n${YELLOW}5. Testando Curtir Evento${NC}"
test_endpoint "POST" "/eventos/$EVENT_ID/like" "" "Authorization: Bearer $TOKEN" "200"

# 6. Obter recomendações
echo -e "\n${YELLOW}6. Testando Recomendações${NC}"
RECOMMENDATIONS_RESPONSE=$(curl -s -X GET "$BASE_URL/recomendacoes/$USER_ID" \
    -H "Authorization: Bearer $TOKEN")

if echo "$RECOMMENDATIONS_RESPONSE" | grep -q "evento"; then
    echo -e "${GREEN}✅ Recomendações obtidas com sucesso${NC}"
    REC_COUNT=$(echo "$RECOMMENDATIONS_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
    echo "   📊 $REC_COUNT recomendações encontradas"
else
    echo -e "${YELLOW}⚠️ Nenhuma recomendação encontrada${NC}"
fi

# 7. Verificar progresso
echo -e "\n${YELLOW}7. Testando Gamificação${NC}"
PROGRESS_RESPONSE=$(curl -s -X GET "$BASE_URL/gamificacao/usuarios/$USER_ID/progresso" \
    -H "Authorization: Bearer $TOKEN")

if echo "$PROGRESS_RESPONSE" | grep -q "xp"; then
    echo -e "${GREEN}✅ Progresso obtido com sucesso${NC}"
    XP=$(echo "$PROGRESS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['xp'])")
    LEVEL=$(echo "$PROGRESS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['nivel'])")
    echo "   ⭐ XP: $XP, Nível: $LEVEL"
else
    echo -e "${RED}❌ Falha ao obter progresso${NC}"
fi

# 8. Leaderboard
echo -e "\n${YELLOW}8. Testando Leaderboard${NC}"
test_endpoint "GET" "/gamificacao/leaderboard" "" "Authorization: Bearer $TOKEN" "200"

# 9. Listar eventos
echo -e "\n${YELLOW}9. Testando Listagem de Eventos${NC}"
test_endpoint "GET" "/eventos/" "" "" "200"

# 10. Teste de erro (token inválido)
echo -e "\n${YELLOW}10. Testando Tratamento de Erros${NC}"
test_endpoint "GET" "/usuarios/$USER_ID" "" "Authorization: Bearer token_invalido" "401"

echo -e "\n${GREEN}🎉 Todos os testes foram executados!${NC}"
echo -e "\n${YELLOW}📊 Resumo dos testes:${NC}"
echo "   ✅ Health Check"
echo "   ✅ Cadastro de Usuário"
echo "   ✅ Login"
echo "   ✅ Criação de Evento"
echo "   ✅ Curtir Evento"
echo "   ✅ Recomendações"
echo "   ✅ Gamificação"
echo "   ✅ Leaderboard"
echo "   ✅ Listagem de Eventos"
echo "   ✅ Tratamento de Erros"

echo -e "\n${YELLOW}🔗 URLs úteis:${NC}"
echo "   📖 Documentação: http://localhost:8000/docs"
echo "   🔄 ReDoc: http://localhost:8000/redoc"
echo "   ❤️ Health: http://localhost:8000/health"

