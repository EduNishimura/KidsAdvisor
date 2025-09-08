# KidsAdvisor - Sistema de Recomendações de Eventos Infantis

## 🎯 Visão Geral

O KidsAdvisor é um sistema completo de recomendações de eventos infantis com gamificação, desenvolvido com FastAPI, MongoDB e algoritmos de recomendação híbridos.

## 🚀 Como Executar

### Opção 1: Docker Compose (Recomendado)

```bash
# Linux/Mac
chmod +x run.sh
./run.sh

# Windows
run.bat
```

### Opção 2: Manual

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Iniciar MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# 3. Executar seed de dados
python seed_data.py

# 4. Iniciar API
uvicorn app.main:app --reload
```

## 📋 Funcionalidades Implementadas

### ✅ Sistema de Usuários

- Cadastro e autenticação JWT
- Perfis de usuários (pais e organizadores)
- Sistema de amizades
- Gamificação com XP, níveis e badges

### ✅ Sistema de Eventos

- Criação e gerenciamento de eventos
- Sistema de curtidas
- Filtros por categoria e localização
- CRUD completo

### ✅ Sistema de Recomendações Híbridas

- **Baseado em Conteúdo**: TF-IDF + Similaridade do Cosseno
- **Colaborativo**: Baseado em eventos curtidos por amigos
- **Híbrido**: 70% conteúdo + 30% colaborativo

### ✅ Gamificação

- Sistema de XP (10 XP por evento curtido)
- 20 níveis diferentes
- 5 badges desbloqueáveis
- Leaderboard global

### ✅ API REST Completa

- Documentação automática (Swagger UI)
- Autenticação JWT
- Validação de dados com Pydantic
- Tratamento de erros

## 🔗 Endpoints Principais

### Usuários

- `POST /usuarios` - Cadastro
- `POST /usuarios/login` - Login
- `GET /usuarios/{id}` - Perfil
- `POST /usuarios/{id}/amigos/{idAmigo}` - Adicionar amigo

### Eventos

- `POST /eventos` - Criar evento
- `GET /eventos` - Listar eventos
- `POST /eventos/{id}/like` - Curtir evento
- `GET /eventos/{id}` - Obter evento

### Recomendações

- `GET /recomendacoes/{usuario_id}` - Recomendações híbridas
- `GET /recomendacoes/{usuario_id}/conteudo` - Baseadas em conteúdo
- `GET /recomendacoes/{usuario_id}/colaborativo` - Colaborativas

### Gamificação

- `GET /gamificacao/usuarios/{id}/progresso` - Progresso do usuário
- `GET /gamificacao/leaderboard` - Ranking global
- `GET /gamificacao/usuarios/{id}/badges` - Badges do usuário

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=app

# Executar testes específicos
pytest tests/test_api.py
```

## 📊 Dados de Exemplo

O sistema inclui dados de exemplo com:

- 5 usuários (4 pais + 1 organizador)
- 8 eventos diversos
- Relacionamentos de amizade
- Eventos curtidos para testar recomendações

### Usuários de Teste

- `maria@gmail.com` (senha: 123456) - XP: 150, Nível: 2
- `joao@gmail.com` (senha: 123456) - XP: 280, Nível: 3
- `ana@gmail.com` (senha: 123456) - XP: 80, Nível: 1
- `pedro@gmail.com` (senha: 123456) - XP: 120, Nível: 2
- `centro@cultural.com` (senha: 123456) - Organizador

## 🏗️ Arquitetura

```
app/
├── main.py              # Ponto de entrada da API
├── database.py          # Conexão MongoDB
├── auth.py              # Autenticação JWT
├── models/              # Schemas Pydantic
│   ├── usuario.py
│   ├── evento.py
│   └── gamificacao.py
├── routers/             # Rotas da API
│   ├── usuarios.py
│   ├── eventos.py
│   ├── recomendacoes.py
│   └── gamificacao.py
└── services/            # Lógica de negócio
    ├── recomendacao.py
    └── gamificacao.py
```

## 🔧 Configuração

### Variáveis de Ambiente

O projeto usa as seguintes variáveis de ambiente (arquivo `.env`):

```bash
# Banco de Dados
MONGODB_URL=mongodb://localhost:27017/kidsadvisor

# Autenticação JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configurações da API
API_PORT=8000
API_HOST=0.0.0.0
DEBUG=True

# Configurações de Recomendação
CONTENT_WEIGHT=0.7
COLLABORATIVE_WEIGHT=0.3
MAX_RECOMMENDATIONS=10

# Configurações de Gamificação
XP_PER_LIKE=10
XP_PER_FRIEND=5
XP_PER_EVENT_CREATED=20
```

### Setup Inicial

```bash
# 1. Copiar arquivo de configuração
cp .env.template .env

# 2. Editar configurações (opcional)
# Os valores padrão funcionam para desenvolvimento

# 3. Executar o projeto
./run.sh  # ou run.bat no Windows
```

## 📈 Algoritmos de Recomendação

### TF-IDF + Similaridade do Cosseno

- Extrai características dos textos dos eventos
- Calcula similaridade entre eventos curtidos e não curtidos
- Recomenda eventos similares

### Filtragem Colaborativa

- Analisa eventos curtidos pelos amigos
- Calcula scores baseados na frequência de likes
- Recomenda eventos populares entre amigos

### Sistema Híbrido

- Combina ambos os métodos
- Peso configurável (70% conteúdo + 30% colaborativo)
- Melhora a qualidade das recomendações

## 🎮 Sistema de Gamificação

### XP e Níveis

- 10 XP por evento curtido
- 20 níveis (0-10450 XP)
- Progresso visual

### Badges

- **Primeiro Passo**: 1 evento curtido
- **Explorador**: 5 eventos curtidos
- **Social**: 3 amigos
- **Veterano**: 20 eventos curtidos
- **Influencer**: Nível 10

### Leaderboard

- Ranking global por XP
- Atualização em tempo real
- Top 10 usuários

## 🐳 Docker

O projeto inclui configuração completa do Docker:

- `Dockerfile` para a API
- `docker-compose.yml` com MongoDB
- Scripts de execução (`run.sh` / `run.bat`)

## 📚 Documentação

Acesse a documentação interativa em:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔒 Segurança

- Autenticação JWT
- Senhas hasheadas com bcrypt
- Validação de dados com Pydantic
- CORS configurado
- Middleware de segurança

## 🚀 Próximos Passos

Possíveis melhorias futuras:

- Sistema de avaliações (1-5 estrelas)
- Recomendações baseadas em localização
- Notificações push
- Interface web frontend
- Sistema de comentários
- Integração com APIs de eventos externos
