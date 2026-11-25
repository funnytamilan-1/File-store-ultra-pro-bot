from .connection import db
from datetime import datetime, timezone

col = db.users


async def add_user(user_id: int):
    now = datetime.now(timezone.utc)
    await col.update_one(
        {"user_id": int(user_id)},
        {"$setOnInsert": {"user_id": int(user_id), "joined_at": now}, "$set": {"last_seen": now}},
        upsert=True,
    )


async def get_user(user_id: int):
    return await col.find_one({"user_id": int(user_id)})


async def get_all_users():
    return col.find({"is_banned": {"$ne": True}}).sort("joined_at", -1)


async def count_users():
    return await col.count_documents({"is_banned": {"$ne": True}})


async def set_user_banned(user_id: int, banned: bool = True):
    await col.update_one({"user_id": int(user_id)}, {"$set": {"is_banned": bool(banned)}}, upsert=True)
