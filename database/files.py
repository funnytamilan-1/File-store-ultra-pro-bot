from .connection import db
from datetime import datetime, timezone

col = db.files


async def save_file(file_id: str, file_name: str, uploader: int, file_type: str = "document", file_size: int = 0, expires_at=None):
    now = datetime.now(timezone.utc)
    values = {
        "file_id": file_id,
        "file_name": file_name or "Telegram file",
        "file_type": file_type,
        "file_size": int(file_size or 0),
        "uploaded_by": int(uploader),
        "uploaded_at": now,
    }
    if expires_at is not None:
        values["expires_at"] = expires_at
    else:
        values["$unset"] = {"expires_at": ""}
    update = {"$set": {k: v for k, v in values.items() if k != "$unset"}}
    if "$unset" in values:
        update["$unset"] = values["$unset"]
    await col.update_one({"file_id": file_id}, update, upsert=True)


async def get_file(file_id: str):
    return await col.find_one({"file_id": file_id})


async def delete_file(file_id: str):
    result = await col.delete_one({"file_id": file_id})
    return result.deleted_count > 0


async def count_files():
    return await col.count_documents({})


async def delete_expired_files():
    now = datetime.now(timezone.utc)
    result = await col.delete_many({"expires_at": {"$lte": now}})
    return result.deleted_count
