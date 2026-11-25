from .connection import db
from config import OWNER_ID

col = db.admins


async def add_admin(user_id: int):
    await col.update_one({"user_id": int(user_id)}, {"$set": {"user_id": int(user_id)}}, upsert=True)


async def remove_admin(user_id: int):
    if int(user_id) == OWNER_ID:
        return False
    result = await col.delete_one({"user_id": int(user_id)})
    return result.deleted_count > 0


async def is_admin(user_id: int):
    if int(user_id) == OWNER_ID:
        return True
    return await col.find_one({"user_id": int(user_id)}, {"_id": 1}) is not None


async def get_all_admins():
    return col.find({}).sort("user_id", 1)


async def count_admins():
    return await col.count_documents({}) + (0 if await col.find_one({"user_id": OWNER_ID}) else 1)
