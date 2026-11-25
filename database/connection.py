from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DATABASE_NAME

if not MONGO_URI:
    raise RuntimeError("MONGO_URI is not configured. Set it in the environment.")

client = AsyncIOMotorClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000,
    connectTimeoutMS=10000,
)
db = client[DATABASE_NAME]
