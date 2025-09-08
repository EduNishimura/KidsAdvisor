# KidsAdvisor API

Sistema de recomendações de eventos infantis com gamificação.

## Stack Tecnológica

- **Backend**: FastAPI (Python 3.11+)
- **Banco de Dados**: MongoDB com conexão assíncrona (Motor)
- **Autenticação**: JWT
- **Recomendações**: TF-IDF + Similaridade do Cosseno + Filtragem Colaborativa
- **Gamificação**: Sistema de XP, badges e leaderboard
- **Infraestrutura**: Docker Compose
- **Testes**: pytest

## Funcionalidades

- Sistema de usuários (pais) com autenticação JWT
- Cadastro e gerenciamento de eventos infantis
- Sistema de amizades entre usuários
- Recomendações híbridas (conteúdo + colaborativo)
- Gamificação com XP, níveis, badges e leaderboard
- API REST completa

## Como executar

### 1. Configurar variáveis de ambiente

```bash
# Copiar arquivo de configuração
cp .env.template .env

# Editar configurações conforme necessário
# (opcional - valores padrão funcionam para desenvolvimento)
```

### 2. Executar com Docker Compose (Recomendado)

```bash
# Linux/Mac
chmod +x run.sh
./run.sh

# Windows
run.bat

# Ou manualmente
docker-compose up --build
```

### 3. Executar localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# Executar seed de dados
python seed_data.py

# Iniciar API
uvicorn app.main:app --reload
```

## Estrutura da API

- `POST /usuarios` - Cadastro de usuário
- `POST /login` - Autenticação
- `GET /usuarios/{id}` - Perfil do usuário
- `POST /usuarios/{id}/amigos/{idAmigo}` - Adicionar amigo
- `POST /eventos` - Criar evento
- `GET /eventos` - Listar eventos
- `POST /eventos/{id}/like` - Curtir evento
- `GET /recomendacoes/{idUsuario}` - Recomendações híbridas
- `GET /usuarios/{id}/progresso` - Progresso do usuário
- `GET /leaderboard` - Ranking global
