import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def connect_to_mongo():
    """Conecta ao MongoDB"""
    db.client = AsyncIOMotorClient(
        os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    )
    db.database = db.client.kidsadvisor
    print("Conectado ao MongoDB")

async def close_mongo_connection():
    """Fecha a conexão com o MongoDB"""
    if db.client:
        db.client.close()
        print("Conexão com MongoDB fechada")

def get_database():
    """Retorna a instância do banco de dados"""
    return db.database
