# 🧪 Guia Completo de Testes e Debug - KidsAdvisor API

## 📋 Índice

1. [Preparação do Ambiente](#preparação-do-ambiente)
2. [Testes com Swagger UI](#testes-com-swagger-ui)
3. [Testes com cURL](#testes-com-curl)
4. [Testes com Python/Requests](#testes-com-pythonrequests)
5. [Debug por Componente](#debug-por-componente)
6. [Testes Automatizados](#testes-automatizados)
7. [Monitoramento e Logs](#monitoramento-e-logs)

---

## 🚀 Preparação do Ambiente

### 1. Iniciar o Projeto

```bash
# Opção 1: Script automático
./run.sh  # Linux/Mac
run.bat   # Windows

# Opção 2: Manual
docker-compose up --build -d
python seed_data.py
```

### 2. Verificar se está funcionando

```bash
# Verificar containers
docker-compose ps

# Verificar logs da API
docker-compose logs api

# Verificar logs do MongoDB
docker-compose logs mongodb

# Testar endpoint básico
curl http://localhost:8000/health
```

---

## 🌐 Testes com Swagger UI

### Acessar Documentação Interativa

- **URL**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Fluxo de Teste Completo no Swagger:

#### 1. **Cadastrar Usuário**

```json
POST /usuarios/
{
  "nome": "João Teste",
  "email": "joao.teste@example.com",
  "senha": "123456",
  "tipo": "pai"
}
```

#### 2. **Fazer Login**

```json
POST /usuarios/login
{
  "email": "joao.teste@example.com",
  "senha": "123456"
}
```

**Copie o `access_token` retornado!**

#### 3. **Criar Evento** (usar token)

```json
POST /eventos/
Authorization: Bearer {seu_token}
{
  "nome": "Evento de Teste",
  "descricao": "Descrição do evento de teste",
  "categoria": "música",
  "localizacao": "São Paulo",
  "data": "2025-12-31T10:00:00",
  "idade_recomendada": "5-10",
  "preco": 25.0,
  "organizadorId": "user_id_do_login"
}
```

#### 4. **Curtir Evento**

```json
POST /eventos/{evento_id}/like
Authorization: Bearer {seu_token}
```

#### 5. **Obter Recomendações**

```json
GET /recomendacoes/{usuario_id}
Authorization: Bearer {seu_token}
```

#### 6. **Verificar Gamificação**

```json
GET /gamificacao/usuarios/{usuario_id}/progresso
Authorization: Bearer {seu_token}
```

---

## 🔧 Testes com cURL

### Script de Teste Completo

```bash
#!/bin/bash
# test_api.sh

BASE_URL="http://localhost:8000"

echo "🧪 Testando KidsAdvisor API..."

# 1. Health Check
echo "1. Health Check"
curl -s "$BASE_URL/health" | jq .

# 2. Cadastrar usuário
echo "2. Cadastrando usuário..."
USER_RESPONSE=$(curl -s -X POST "$BASE_URL/usuarios/" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Teste",
    "email": "maria.teste@example.com",
    "senha": "123456",
    "tipo": "pai"
  }')

echo $USER_RESPONSE | jq .
USER_ID=$(echo $USER_RESPONSE | jq -r '.id')

# 3. Login
echo "3. Fazendo login..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/usuarios/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "maria.teste@example.com",
    "senha": "123456"
  }')

echo $LOGIN_RESPONSE | jq .
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

# 4. Criar evento
echo "4. Criando evento..."
EVENT_RESPONSE=$(curl -s -X POST "$BASE_URL/eventos/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "nome": "Show Infantil Teste",
    "descricao": "Apresentação musical para crianças",
    "categoria": "música",
    "localizacao": "São Paulo",
    "data": "2025-12-31T10:00:00",
    "idade_recomendada": "5-10",
    "preco": 30.0,
    "organizadorId": "'$USER_ID'"
  }')

echo $EVENT_RESPONSE | jq .
EVENT_ID=$(echo $EVENT_RESPONSE | jq -r '.id')

# 5. Curtir evento
echo "5. Curtindo evento..."
curl -s -X POST "$BASE_URL/eventos/$EVENT_ID/like" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 6. Obter recomendações
echo "6. Obtendo recomendações..."
curl -s -X GET "$BASE_URL/recomendacoes/$USER_ID" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 7. Verificar progresso
echo "7. Verificando progresso..."
curl -s -X GET "$BASE_URL/gamificacao/usuarios/$USER_ID/progresso" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 8. Leaderboard
echo "8. Verificando leaderboard..."
curl -s -X GET "$BASE_URL/gamificacao/leaderboard" \
  -H "Authorization: Bearer $TOKEN" | jq .

echo "✅ Testes concluídos!"
```

---

## 🐍 Testes com Python/Requests

### Script de Teste Python

```python
# test_api.py
import requests
import json
import time

BASE_URL = "http://localhost:8000"

class KidsAdvisorTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None

    def test_health(self):
        """Testa endpoint de health"""
        print("🏥 Testando Health Check...")
        response = self.session.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200

    def create_user(self):
        """Cria usuário de teste"""
        print("👤 Criando usuário...")
        user_data = {
            "nome": "Ana Teste",
            "email": f"ana.teste.{int(time.time())}@example.com",
            "senha": "123456",
            "tipo": "pai"
        }

        response = self.session.post(f"{BASE_URL}/usuarios/", json=user_data)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            user_info = response.json()
            self.user_id = user_info["id"]
            print(f"Usuário criado: {user_info['nome']} (ID: {self.user_id})")
            return True
        else:
            print(f"Erro: {response.text}")
            return False

    def login(self, email, password):
        """Faz login e obtém token"""
        print("🔐 Fazendo login...")
        login_data = {"email": email, "senha": password}

        response = self.session.post(f"{BASE_URL}/usuarios/login", json=login_data)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            token_info = response.json()
            self.token = token_info["access_token"]
            print("Login realizado com sucesso!")
            return True
        else:
            print(f"Erro no login: {response.text}")
            return False

    def create_event(self):
        """Cria evento de teste"""
        print("🎪 Criando evento...")
        event_data = {
            "nome": "Workshop de Arte Teste",
            "descricao": "Atividade criativa para crianças",
            "categoria": "arte",
            "localizacao": "São Paulo",
            "data": "2025-12-31T14:00:00",
            "idade_recomendada": "6-12",
            "preco": 25.0,
            "organizadorId": self.user_id
        }

        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.session.post(f"{BASE_URL}/eventos/", json=event_data, headers=headers)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            event_info = response.json()
            print(f"Evento criado: {event_info['nome']} (ID: {event_info['id']})")
            return event_info["id"]
        else:
            print(f"Erro: {response.text}")
            return None

    def like_event(self, event_id):
        """Curtir evento"""
        print(f"❤️ Curtindo evento {event_id}...")
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.session.post(f"{BASE_URL}/eventos/{event_id}/like", headers=headers)
        print(f"Status: {response.status_code}")
        return response.status_code == 200

    def get_recommendations(self):
        """Obtém recomendações"""
        print("🎯 Obtendo recomendações...")
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.session.get(f"{BASE_URL}/recomendacoes/{self.user_id}", headers=headers)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            recommendations = response.json()
            print(f"Recomendações encontradas: {len(recommendations)}")
            for i, rec in enumerate(recommendations[:3]):
                print(f"  {i+1}. {rec['evento']['nome']} (Score: {rec['score']:.3f})")
            return recommendations
        else:
            print(f"Erro: {response.text}")
            return []

    def get_progress(self):
        """Obtém progresso do usuário"""
        print("📊 Verificando progresso...")
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.session.get(f"{BASE_URL}/gamificacao/usuarios/{self.user_id}/progresso", headers=headers)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            progress = response.json()
            print(f"XP: {progress['xp']}, Nível: {progress['nivel']}")
            print(f"Badges: {progress['badges']}")
            return progress
        else:
            print(f"Erro: {response.text}")
            return None

    def run_full_test(self):
        """Executa teste completo"""
        print("🚀 Iniciando teste completo da API KidsAdvisor...")

        # Teste sequencial
        if not self.test_health():
            print("❌ Health check falhou!")
            return False

        if not self.create_user():
            print("❌ Criação de usuário falhou!")
            return False

        if not self.login(f"ana.teste.{int(time.time())}@example.com", "123456"):
            print("❌ Login falhou!")
            return False

        event_id = self.create_event()
        if not event_id:
            print("❌ Criação de evento falhou!")
            return False

        if not self.like_event(event_id):
            print("❌ Curtir evento falhou!")
            return False

        recommendations = self.get_recommendations()
        if not recommendations:
            print("⚠️ Nenhuma recomendação encontrada")

        progress = self.get_progress()
        if not progress:
            print("❌ Obter progresso falhou!")
            return False

        print("✅ Teste completo realizado com sucesso!")
        return True

if __name__ == "__main__":
    tester = KidsAdvisorTester()
    tester.run_full_test()
```

---

## 🔍 Debug por Componente

### 1. **Debug da Conexão MongoDB**

```python
# debug_database.py
import asyncio
from app.database import connect_to_mongo, get_database

async def test_database():
    print("🔌 Testando conexão MongoDB...")

    try:
        await connect_to_mongo()
        db = get_database()

        # Testar inserção
        result = await db.test_collection.insert_one({"test": "data"})
        print(f"✅ Inserção OK: {result.inserted_id}")

        # Testar busca
        doc = await db.test_collection.find_one({"_id": result.inserted_id})
        print(f"✅ Busca OK: {doc}")

        # Limpar teste
        await db.test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Limpeza OK")

    except Exception as e:
        print(f"❌ Erro na conexão: {e}")

asyncio.run(test_database())
```

### 2. **Debug da Autenticação JWT**

```python
# debug_auth.py
from app.auth import create_access_token, verify_password, get_password_hash
from datetime import timedelta

def test_auth():
    print("🔐 Testando autenticação...")

    # Teste hash de senha
    password = "123456"
    hashed = get_password_hash(password)
    print(f"✅ Hash gerado: {hashed[:20]}...")

    # Teste verificação
    is_valid = verify_password(password, hashed)
    print(f"✅ Verificação: {is_valid}")

    # Teste token JWT
    token = create_access_token({"sub": "test_user"}, timedelta(minutes=30))
    print(f"✅ Token gerado: {token[:50]}...")

    # Teste decodificação
    from jose import jwt
    payload = jwt.decode(token, "your-super-secret-key-change-in-production", algorithms=["HS256"])
    print(f"✅ Token decodificado: {payload}")

test_auth()
```

### 3. **Debug do Sistema de Recomendações**

```python
# debug_recommendations.py
import asyncio
from app.services.recomendacao import RecomendacaoService
from app.database import connect_to_mongo, get_database

async def test_recommendations():
    print("🎯 Testando sistema de recomendações...")

    await connect_to_mongo()
    db = get_database()

    # Obter usuário de teste
    user = await db.usuarios.find_one({"email": "maria@gmail.com"})
    if not user:
        print("❌ Usuário de teste não encontrado")
        return

    print(f"👤 Usuário: {user['nome']}")
    print(f"📝 Eventos curtidos: {len(user.get('eventosCurtidos', []))}")
    print(f"👥 Amigos: {len(user.get('amigos', []))}")

    # Testar recomendações
    service = RecomendacaoService()

    # Recomendações de conteúdo
    content_recs = await service._recomendacoes_por_conteudo(user, [])
    print(f"📊 Recomendações de conteúdo: {len(content_recs)}")

    # Recomendações colaborativas
    collab_recs = await service._recomendacoes_colaborativas(user, [])
    print(f"👥 Recomendações colaborativas: {len(collab_recs)}")

    # Recomendações híbridas
    hybrid_recs = await service.obter_recomendacoes_hibridas(str(user["_id"]), 5)
    print(f"🎯 Recomendações híbridas: {len(hybrid_recs)}")

    for i, rec in enumerate(hybrid_recs[:3]):
        print(f"  {i+1}. {rec.evento.nome} (Score: {rec.score:.3f})")

asyncio.run(test_recommendations())
```

### 4. **Debug da Gamificação**

```python
# debug_gamification.py
import asyncio
from app.services.gamificacao import GamificacaoService
from app.database import connect_to_mongo, get_database

async def test_gamification():
    print("🎮 Testando sistema de gamificação...")

    await connect_to_mongo()
    db = get_database()

    # Obter usuário de teste
    user = await db.usuarios.find_one({"email": "joao@gmail.com"})
    if not user:
        print("❌ Usuário de teste não encontrado")
        return

    print(f"👤 Usuário: {user['nome']}")
    print(f"⭐ XP atual: {user.get('xp', 0)}")
    print(f"🏆 Nível atual: {user.get('nivel', 1)}")
    print(f"🎖️ Badges: {user.get('badges', [])}")

    # Testar serviço de gamificação
    service = GamificacaoService()

    # Calcular nível
    nivel = await service.calcular_nivel(user.get('xp', 0))
    print(f"📊 Nível calculado: {nivel}")

    # Próximo nível
    prox_xp = await service.obter_proximo_nivel_xp(nivel)
    print(f"🎯 XP para próximo nível: {prox_xp}")

    # Verificar badges
    novos_badges = await service.verificar_badges(str(user["_id"]))
    print(f"🆕 Novos badges: {novos_badges}")

    # Progresso completo
    progresso = await service.obter_progresso_usuario(str(user["_id"]))
    print(f"📈 Progresso: {progresso}")

asyncio.run(test_gamification())
```

---

## 🧪 Testes Automatizados

### Executar Testes com pytest

```bash
# Executar todos os testes
pytest

# Executar com verbose
pytest -v

# Executar com cobertura
pytest --cov=app

# Executar testes específicos
pytest tests/test_api.py::TestUsuarios::test_criar_usuario

# Executar com relatório HTML
pytest --cov=app --cov-report=html
```

### Teste de Performance

```python
# test_performance.py
import time
import requests
import concurrent.futures

def test_endpoint_performance():
    """Testa performance dos endpoints principais"""
    base_url = "http://localhost:8000"

    endpoints = [
        "/health",
        "/usuarios/",
        "/eventos/",
        "/gamificacao/leaderboard"
    ]

    def test_endpoint(endpoint):
        start_time = time.time()
        try:
            response = requests.get(f"{base_url}{endpoint}")
            end_time = time.time()
            return {
                "endpoint": endpoint,
                "status": response.status_code,
                "time": end_time - start_time,
                "success": True
            }
        except Exception as e:
            end_time = time.time()
            return {
                "endpoint": endpoint,
                "status": "error",
                "time": end_time - start_time,
                "success": False,
                "error": str(e)
            }

    # Teste sequencial
    print("🔄 Teste sequencial:")
    for endpoint in endpoints:
        result = test_endpoint(endpoint)
        print(f"  {endpoint}: {result['time']:.3f}s ({result['status']})")

    # Teste concorrente
    print("\n⚡ Teste concorrente (10 requisições):")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(test_endpoint, endpoint) for endpoint in endpoints * 3]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    for result in results:
        print(f"  {result['endpoint']}: {result['time']:.3f}s ({result['status']})")

if __name__ == "__main__":
    test_endpoint_performance()
```

---

## 📊 Monitoramento e Logs

### 1. **Logs do Docker**

```bash
# Ver logs em tempo real
docker-compose logs -f api

# Ver logs do MongoDB
docker-compose logs -f mongodb

# Ver logs de todos os serviços
docker-compose logs -f
```

### 2. **Monitoramento de Performance**

```bash
# Verificar uso de recursos
docker stats

# Verificar processos dentro do container
docker-compose exec api ps aux

# Verificar conexões de rede
docker-compose exec api netstat -tulpn
```

### 3. **Debug de Erros Comuns**

#### Erro de Conexão MongoDB

```bash
# Verificar se MongoDB está rodando
docker-compose ps mongodb

# Verificar logs do MongoDB
docker-compose logs mongodb

# Testar conexão manual
docker-compose exec api python -c "
import asyncio
from app.database import connect_to_mongo
asyncio.run(connect_to_mongo())
"
```

#### Erro de Autenticação JWT

```bash
# Verificar variáveis de ambiente
docker-compose exec api env | grep JWT

# Testar criação de token
docker-compose exec api python -c "
from app.auth import create_access_token
from datetime import timedelta
print(create_access_token({'sub': 'test'}, timedelta(minutes=30)))
"
```

#### Erro de Recomendações

```bash
# Verificar dados de exemplo
docker-compose exec api python -c "
import asyncio
from app.database import get_database
async def check_data():
    db = get_database()
    users = await db.usuarios.count_documents({})
    events = await db.eventos.count_documents({})
    print(f'Usuários: {users}, Eventos: {events}')
asyncio.run(check_data())
"
```

---

## 🎯 Checklist de Testes

### ✅ Testes Básicos

- [ ] Health check responde
- [ ] Swagger UI carrega
- [ ] Cadastro de usuário funciona
- [ ] Login retorna token
- [ ] Criação de evento funciona
- [ ] Curtir evento funciona
- [ ] Recomendações retornam dados
- [ ] Gamificação funciona

### ✅ Testes de Integração

- [ ] Fluxo completo usuário → evento → like → recomendação
- [ ] Sistema de amizades
- [ ] Badges são concedidos
- [ ] Leaderboard atualiza
- [ ] Autenticação JWT funciona

### ✅ Testes de Performance

- [ ] API responde em < 1s
- [ ] MongoDB conecta rapidamente
- [ ] Recomendações calculam em tempo aceitável
- [ ] Múltiplas requisições simultâneas

### ✅ Testes de Erro

- [ ] Usuário inexistente
- [ ] Token inválido
- [ ] Dados inválidos
- [ ] Evento inexistente
- [ ] Permissões incorretas

---

## 🚀 Próximos Passos

1. **Implementar testes de carga** com ferramentas como Locust
2. **Adicionar métricas** com Prometheus/Grafana
3. **Implementar CI/CD** com GitHub Actions
4. **Adicionar testes de segurança** com OWASP ZAP
5. **Implementar monitoramento** com APM tools

---

**🎉 Com este guia, você pode testar completamente a API KidsAdvisor e fazer debug de qualquer problema que surgir!**

