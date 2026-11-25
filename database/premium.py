from datetime import datetime, timedelta, timezone
from .connection import db

col = db.premium


async def add_premium(user_id: int, days: int):
    if int(days) < 1:
        raise ValueError("Premium duration must be at least one day.")
    now = datetime.now(timezone.utc)
    existing = await col.find_one({"user_id": int(user_id)})
    current_expiry = existing.get("expiry") if existing else None
    if current_expiry and current_expiry > now:
        expiry_date = current_expiry + timedelta(days=int(days))
    else:
        expiry_date = now + timedelta(days=int(days))
    await col.update_one(
        {"user_id": int(user_id)},
        {"$set": {"user_id": int(user_id), "expiry": expiry_date}},
        upsert=True,
    )
    return expiry_date


async def remove_premium(user_id: int):
    result = await col.delete_one({"user_id": int(user_id)})
    return result.deleted_count > 0


async def is_premium(user_id: int):
    user = await col.find_one({"user_id": int(user_id), "expiry": {"$gt": datetime.now(timezone.utc)}})
    return user is not None


async def get_premium_users():
    return await col.find({"expiry": {"$gt": datetime.now(timezone.utc)}}).to_list(length=None)


async def get_all_premium():
    return col.find({}).sort("expiry", -1)


async def count_premium_users():
    return await col.count_documents({"expiry": {"$gt": datetime.now(timezone.utc)}})


async def remove_expired_premium():
    result = await col.delete_many({"expiry": {"$lte": datetime.now(timezone.utc)}})
    return result.deleted_count
