import asyncio
import os
from datetime import datetime, timedelta
from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.auth import get_password_hash
from bson import ObjectId
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

async def seed_database():
    """Insere dados de exemplo no banco de dados"""
    await connect_to_mongo()
    db = get_database()
    
    # Limpar dados existentes
    await db.usuarios.delete_many({})
    await db.eventos.delete_many({})
    
    print("Inserindo usuários de exemplo...")
    
    # Criar usuários de exemplo
    usuarios_exemplo = [
        {
            "_id": "user001",
            "nome": "Maria Silva",
            "email": "maria@gmail.com",
            "senha": get_password_hash("123456"),
            "tipo": "pai",
            "amigos": ["user002", "user003"],
            "eventosCurtidos": ["ev001", "ev003"],
            "xp": 150,
            "nivel": 2,
            "badges": ["primeiro_evento", "explorador"],
            "data_criacao": datetime.utcnow()
        },
        {
            "_id": "user002",
            "nome": "João Santos",
            "email": "joao@gmail.com",
            "senha": get_password_hash("123456"),
            "tipo": "pai",
            "amigos": ["user001", "user004"],
            "eventosCurtidos": ["ev002", "ev004", "ev005"],
            "xp": 280,
            "nivel": 3,
            "badges": ["primeiro_evento", "explorador", "social"],
            "data_criacao": datetime.utcnow()
        },
        {
            "_id": "user003",
            "nome": "Ana Costa",
            "email": "ana@gmail.com",
            "senha": get_password_hash("123456"),
            "tipo": "pai",
            "amigos": ["user001"],
            "eventosCurtidos": ["ev001", "ev002"],
            "xp": 80,
            "nivel": 1,
            "badges": ["primeiro_evento"],
            "data_criacao": datetime.utcnow()
        },
        {
            "_id": "user004",
            "nome": "Pedro Oliveira",
            "email": "pedro@gmail.com",
            "senha": get_password_hash("123456"),
            "tipo": "pai",
            "amigos": ["user002"],
            "eventosCurtidos": ["ev003", "ev004"],
            "xp": 120,
            "nivel": 2,
            "badges": ["primeiro_evento"],
            "data_criacao": datetime.utcnow()
        },
        {
            "_id": "org001",
            "nome": "Centro Cultural SP",
            "email": "centro@cultural.com",
            "senha": get_password_hash("123456"),
            "tipo": "organizador",
            "amigos": [],
            "eventosCurtidos": [],
            "xp": 0,
            "nivel": 1,
            "badges": [],
            "data_criacao": datetime.utcnow()
        }
    ]
    
    await db.usuarios.insert_many(usuarios_exemplo)
    print(f"Inseridos {len(usuarios_exemplo)} usuários")
    
    print("Inserindo eventos de exemplo...")
    
    # Criar eventos de exemplo
    eventos_exemplo = [
        {
            "_id": "ev001",
            "nome": "Show Infantil - Banda do Mar",
            "descricao": "Apresentação musical interativa para crianças de 3 a 10 anos com músicas educativas sobre o meio ambiente",
            "categoria": "música",
            "localizacao": "São Paulo",
            "data": datetime.utcnow() + timedelta(days=15),
            "idade_recomendada": "3-10",
            "preco": 45.0,
            "organizadorId": "org001",
            "likes": 12,
            "data_criacao": datetime.utcnow()
        },
        {
            "_id": "ev002",
            "nome": "Teatro: A Princesa e o Dragão",
            "descricao": "Espetáculo teatral infantil com fantoches e interação com o público sobre amizade e coragem",
            "categoria": "teatro",
            "localizacao": "Rio de Janeiro",
            "data": datetime.utcnow() + timedelta(days=20),
            "idade_recomendada": "4-12",
            "preco": 35.0,
            "organizadorId": "org001",
            "likes": 8,
            "data_criacao": datetime.utcnow()
        },
        {
            "_id": "ev003",
            "nome": "Workshop de Arte - Pintura com Dedos",
            "descricao": "Atividade criativa onde crianças aprendem técnicas básicas de pintura usando os dedos",
            "categoria": "arte",
            "localizacao": "São Paulo",
            "data": datetime.utcnow() + timedelta(days=25),
            "idade_recomendada": "2-8",
            "preco": 25.0,
            "organizadorId": "org001",
            "likes": 15,
            "data_criacao": datetime.utcnow()
        },
        {
            "_id": "ev004",
            "nome": "Contação de Histórias - Era Uma Vez",
            "descricao": "Sessão de contação de histórias clássicas com fantoches e música ao vivo",
            "categoria": "literatura",
            "localizacao": "Belo Horizonte",
            "data": datetime.utcnow() + timedelta(days=30),
            "idade_recomendada": "3-9",
            "preco": 20.0,
            "organizadorId": "org001",
            "likes": 6,
            "data_criacao": datetime.utcnow()
        },
        {
            "_id": "ev005",
            "nome": "Circuito de Brincadeiras",
            "descricao": "Espaço com diversas brincadeiras tradicionais como amarelinha, pula corda e pega-pega",
            "categoria": "esporte",
            "localizacao": "São Paulo",
            "data": datetime.utcnow() + timedelta(days=35),
            "idade_recomendada": "5-12",
            "preco": 15.0,
            "organizadorId": "org001",
            "likes": 22,
            "data_criacao": datetime.utcnow()
        },
        {
            "_id": "ev006",
            "nome": "Aula de Culinária Infantil",
            "descricao": "Workshop onde crianças aprendem a fazer biscoitos e cupcakes com ingredientes saudáveis",
            "categoria": "culinária",
            "localizacao": "São Paulo",
            "data": datetime.utcnow() + timedelta(days=40),
            "idade_recomendada": "6-12",
            "preco": 50.0,
            "organizadorId": "org001",
            "likes": 9,
            "data_criacao": datetime.utcnow()
        },
        {
            "_id": "ev007",
            "nome": "Sessão de Cinema - Filmes Educativos",
            "descricao": "Exibição de filmes infantis educativos seguida de debate sobre os temas abordados",
            "categoria": "cinema",
            "localizacao": "Rio de Janeiro",
            "data": datetime.utcnow() + timedelta(days=45),
            "idade_recomendada": "7-14",
            "preco": 30.0,
            "organizadorId": "org001",
            "likes": 4,
            "data_criacao": datetime.utcnow()
        },
        {
            "_id": "ev008",
            "nome": "Oficina de Robótica para Crianças",
            "descricao": "Introdução à programação e robótica através de brinquedos educativos e jogos",
            "categoria": "tecnologia",
            "localizacao": "São Paulo",
            "data": datetime.utcnow() + timedelta(days=50),
            "idade_recomendada": "8-14",
            "preco": 80.0,
            "organizadorId": "org001",
            "likes": 18,
            "data_criacao": datetime.utcnow()
        }
    ]
    
    await db.eventos.insert_many(eventos_exemplo)
    print(f"Inseridos {len(eventos_exemplo)} eventos")
    
    print("Seed concluído com sucesso!")
    print("\nUsuários criados:")
    print("- maria@gmail.com (senha: 123456)")
    print("- joao@gmail.com (senha: 123456)")
    print("- ana@gmail.com (senha: 123456)")
    print("- pedro@gmail.com (senha: 123456)")
    print("- centro@cultural.com (senha: 123456)")

if __name__ == "__main__":
    asyncio.run(seed_database())
