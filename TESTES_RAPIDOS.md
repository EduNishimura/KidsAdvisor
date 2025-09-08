# 🚀 Guia Rápido de Testes - KidsAdvisor API

## ⚡ Testes Rápidos

### 1. **Iniciar o Projeto**

```bash
# Opção 1: Script automático
./run.sh  # Linux/Mac
run.bat   # Windows

# Opção 2: Manual
docker-compose up --build -d
python seed_data.py
```

### 2. **Teste Básico (Swagger UI)**

- Acesse: http://localhost:8000/docs
- Teste o fluxo: Cadastro → Login → Criar Evento → Curtir → Recomendações

### 3. **Teste Automatizado (Bash)**

```bash
# Teste completo com cURL
./test_api.sh
```

### 4. **Teste Automatizado (Python)**

```bash
# Teste completo com Python
python test_api.py
```

### 5. **Debug Completo**

```bash
# Debug de todos os componentes
python debug_api.py
```

## 🔍 Debug Específico

### **Problema: API não responde**

```bash
# Verificar containers
docker-compose ps

# Ver logs
docker-compose logs api

# Testar health
curl http://localhost:8000/health
```

### **Problema: MongoDB não conecta**

```bash
# Verificar MongoDB
docker-compose logs mongodb

# Testar conexão
docker-compose exec api python -c "
import asyncio
from app.database import connect_to_mongo
asyncio.run(connect_to_mongo())
"
```

### **Problema: Autenticação falha**

```bash
# Verificar variáveis
docker-compose exec api env | grep JWT

# Testar token
docker-compose exec api python -c "
from app.auth import create_access_token
from datetime import timedelta
print(create_access_token({'sub': 'test'}, timedelta(minutes=30)))
"
```

### **Problema: Recomendações não funcionam**

```bash
# Verificar dados
docker-compose exec api python -c "
import asyncio
from app.database import get_database
async def check():
    db = get_database()
    users = await db.usuarios.count_documents({})
    events = await db.eventos.count_documents({})
    print(f'Usuários: {users}, Eventos: {events}')
asyncio.run(check())
"
```

## 📊 Testes de Performance

### **Teste de Carga Simples**

```bash
# Múltiplas requisições simultâneas
for i in {1..10}; do
  curl -s http://localhost:8000/health &
done
wait
```

### **Monitoramento**

```bash
# Ver uso de recursos
docker stats

# Ver logs em tempo real
docker-compose logs -f api
```

## 🧪 Testes com pytest

```bash
# Executar todos os testes
pytest

# Executar com verbose
pytest -v

# Executar com cobertura
pytest --cov=app

# Executar testes específicos
pytest tests/test_api.py::TestUsuarios::test_criar_usuario
```

## 🔗 URLs Úteis

- **📖 Swagger UI**: http://localhost:8000/docs
- **🔄 ReDoc**: http://localhost:8000/redoc
- **❤️ Health**: http://localhost:8000/health
- **🏠 API Root**: http://localhost:8000/

## 📝 Checklist de Testes

### ✅ Testes Básicos

- [ ] Health check responde (200)
- [ ] Swagger UI carrega
- [ ] Cadastro de usuário funciona
- [ ] Login retorna token JWT
- [ ] Criação de evento funciona
- [ ] Curtir evento adiciona XP
- [ ] Recomendações retornam dados
- [ ] Gamificação funciona

### ✅ Testes de Integração

- [ ] Fluxo completo: usuário → evento → like → recomendação
- [ ] Sistema de amizades
- [ ] Badges são concedidos automaticamente
- [ ] Leaderboard atualiza corretamente
- [ ] Autenticação JWT em todas as rotas protegidas

### ✅ Testes de Erro

- [ ] Usuário inexistente (404)
- [ ] Token inválido (401)
- [ ] Dados inválidos (422)
- [ ] Evento inexistente (404)
- [ ] Permissões incorretas (403)

## 🚨 Problemas Comuns

### **"Connection refused"**

- Verificar se Docker está rodando
- Executar `docker-compose up --build`

### **"Module not found"**

- Verificar se está no diretório correto
- Executar `pip install -r requirements.txt`

### **"MongoDB connection failed"**

- Verificar se MongoDB está rodando
- Verificar variáveis de ambiente

### **"JWT token invalid"**

- Verificar SECRET_KEY no .env
- Verificar se token não expirou

## 🎯 Próximos Passos

1. **Implementar testes de carga** com Locust
2. **Adicionar métricas** com Prometheus
3. **Implementar CI/CD** com GitHub Actions
4. **Adicionar testes de segurança**
5. **Implementar monitoramento** com APM

---

**🎉 Com este guia, você pode testar completamente a API KidsAdvisor!**

