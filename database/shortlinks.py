from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError
from .connection import db
from utils.helpers import generate_token

col = db.shortlinks


async def create_shortlink(target_url: str, created_by: int, slug: str = None):
    if not target_url.startswith(("https://", "http://")):
        raise ValueError("Short-link destination must be an http(s) URL.")
    await col.create_index("slug", unique=True)

    custom_slug = slug.strip() if slug else None
    if custom_slug and (not custom_slug.isalnum() or len(custom_slug) < 4 or len(custom_slug) > 32):
        raise ValueError("Custom short code must be 4-32 letters or numbers.")

    for _ in range(10):
        candidate = custom_slug or generate_token(8)
        document = {
            "slug": candidate,
            "target_url": target_url,
            "created_by": int(created_by),
            "created_at": datetime.now(timezone.utc),
            "clicks": 0,
        }
        try:
            await col.insert_one(document)
            return document
        except DuplicateKeyError:
            if custom_slug:
                raise ValueError("That short code is already in use.")
    raise RuntimeError("Could not allocate a unique short code. Please retry.")


async def get_shortlink(slug: str):
    return await col.find_one({"slug": slug})


async def record_shortlink_click(slug: str):
    await col.update_one(
        {"slug": slug},
        {"$inc": {"clicks": 1}, "$set": {"last_clicked": datetime.now(timezone.utc)}},
    )


async def count_shortlinks():
    return await col.count_documents({})


async def get_recent_shortlinks(limit: int = 200):
    return col.find({}).sort("created_at", -1).limit(max(1, min(int(limit), 500)))
