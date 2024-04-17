import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DB_URL = "mongodb+srv://RDGalihRakasiwi:RDGalihRakasiwi@cluster0.ni5ltny.mongodb.net/"
MONGO_DB_NAME = "dira_abinawa-all"

# Async Function
async def get_database() -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(MONGO_DB_URL)
    database = client[MONGO_DB_NAME]
    return database