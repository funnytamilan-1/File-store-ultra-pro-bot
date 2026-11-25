from datetime import datetime, timezone
from .connection import db
from utils.helpers import generate_token

col = db.shortlinks


async def create_shortlink(target_url: str, created_by: int, slug: str = None):
    if not target_url.startswith(("https://", "http://")):
        raise ValueError("Short-link destination must be an http(s) URL.")
    if slug:
        slug = slug.strip()
        if not slug.isalnum() or len(slug) < 4 or len(slug) > 32:
            raise ValueError("Custom short code must be 4-32 letters or numbers.")
        if await col.find_one({"slug": slug}):
            raise ValueError("That short code is already in use.")
    else:
        for _ in range(10):
            candidate = generate_token(8)
            if not await col.find_one({"slug": candidate}):
                slug = candidate
                break
        if not slug:
            raise RuntimeError("Could not allocate a unique short code. Please retry.")

    document = {
        "slug": slug,
        "target_url": target_url,
        "created_by": int(created_by),
        "created_at": datetime.now(timezone.utc),
        "clicks": 0,
    }
    await col.insert_one(document)
    return document


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
