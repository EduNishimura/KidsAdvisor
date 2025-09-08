import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.database import connect_to_mongo, close_mongo_connection
from app.auth import get_password_hash
from bson import ObjectId

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def setup_database():
    """Setup test database"""
    await connect_to_mongo()
    yield
    await close_mongo_connection()

@pytest.fixture
async def client(setup_database):
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def test_user():
    """Create a test user"""
    from app.database import get_database
    db = get_database()
    
    user_data = {
        "_id": "test_user_001",
        "nome": "Test User",
        "email": "test@example.com",
        "senha": get_password_hash("testpassword"),
        "tipo": "pai",
        "amigos": [],
        "eventosCurtidos": [],
        "xp": 0,
        "nivel": 1,
        "badges": []
    }
    
    await db.usuarios.insert_one(user_data)
    return user_data

@pytest.fixture
async def test_event():
    """Create a test event"""
    from app.database import get_database
    db = get_database()
    
    event_data = {
        "_id": "test_event_001",
        "nome": "Test Event",
        "descricao": "Test event description",
        "categoria": "test",
        "localizacao": "Test City",
        "data": "2025-12-31T10:00:00",
        "idade_recomendada": "5-10",
        "preco": 25.0,
        "organizadorId": "test_user_001",
        "likes": 0
    }
    
    await db.eventos.insert_one(event_data)
    return event_data

@pytest.fixture
async def auth_token(client, test_user):
    """Get authentication token"""
    response = await client.post("/usuarios/login", json={
        "email": "test@example.com",
        "senha": "testpassword"
    })
    return response.json()["access_token"]

class TestUsuarios:
    async def test_criar_usuario(self, client):
        """Test user creation"""
        user_data = {
            "nome": "New User",
            "email": "newuser@example.com",
            "senha": "password123",
            "tipo": "pai"
        }
        
        response = await client.post("/usuarios/", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["nome"] == user_data["nome"]
        assert data["email"] == user_data["email"]
        assert data["tipo"] == user_data["tipo"]
        assert data["xp"] == 0
        assert data["nivel"] == 1

    async def test_login_usuario(self, client, test_user):
        """Test user login"""
        login_data = {
            "email": "test@example.com",
            "senha": "testpassword"
        }
        
        response = await client.post("/usuarios/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_usuario_invalido(self, client):
        """Test invalid login"""
        login_data = {
            "email": "invalid@example.com",
            "senha": "wrongpassword"
        }
        
        response = await client.post("/usuarios/login", json=login_data)
        assert response.status_code == 401

    async def test_obter_usuario(self, client, test_user, auth_token):
        """Test get user profile"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = await client.get(f"/usuarios/{test_user['_id']}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["nome"] == test_user["nome"]
        assert data["email"] == test_user["email"]

class TestEventos:
    async def test_criar_evento(self, client, test_user, auth_token):
        """Test event creation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        event_data = {
            "nome": "New Event",
            "descricao": "New event description",
            "categoria": "music",
            "localizacao": "São Paulo",
            "data": "2025-12-31T10:00:00",
            "idade_recomendada": "5-10",
            "preco": 30.0,
            "organizadorId": test_user["_id"]
        }
        
        response = await client.post("/eventos/", json=event_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["nome"] == event_data["nome"]
        assert data["likes"] == 0

    async def test_listar_eventos(self, client, test_event):
        """Test list events"""
        response = await client.get("/eventos/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        assert any(event["nome"] == test_event["nome"] for event in data)

    async def test_curtir_evento(self, client, test_user, test_event, auth_token):
        """Test like event"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = await client.post(f"/eventos/{test_event['_id']}/like", headers=headers)
        assert response.status_code == 200
        
        # Verify XP was added
        from app.database import get_database
        db = get_database()
        updated_user = await db.usuarios.find_one({"_id": test_user["_id"]})
        assert updated_user["xp"] == 10
        assert test_event["_id"] in updated_user["eventosCurtidos"]

class TestGamificacao:
    async def test_obter_progresso(self, client, test_user, auth_token):
        """Test get user progress"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = await client.get(f"/gamificacao/usuarios/{test_user['_id']}/progresso", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["usuario_id"] == test_user["_id"]
        assert data["xp"] == test_user["xp"]
        assert data["nivel"] == test_user["nivel"]

    async def test_leaderboard(self, client, auth_token):
        """Test leaderboard"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = await client.get("/gamificacao/leaderboard", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
