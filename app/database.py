import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://edunish:Projeto01@cluster0.oteilom.mongodb.net")
DB_NAME = os.environ.get("MONGO_DB", "kidsadvisor")


client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]