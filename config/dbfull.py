import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DB_URL = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.0.2"
MONGO_DB_NAME = "db-test"

# Async Function
async def get_database() -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(MONGO_DB_URL)
    database = client[MONGO_DB_NAME]
    return database