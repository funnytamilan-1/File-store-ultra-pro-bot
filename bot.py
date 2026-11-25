import asyncio
import logging
from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN, validate_config
from database.premium import remove_expired_premium
from database.files import delete_expired_files

validate_config()
logging.basicConfig(level=logging.INFO)

app = Client("FileStoreBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, plugins={"root": "plugins"})


async def cleanup_loop():
    while True:
        try:
            expired_premium = await remove_expired_premium()
            expired_files = await delete_expired_files()
            if expired_premium or expired_files:
                logging.info("Expiry cleanup removed %s premium records and %s file records", expired_premium, expired_files)
        except Exception:
            logging.exception("Scheduled cleanup failed")
        await asyncio.sleep(3600)


async def main():
    await app.start()
    cleanup_task = asyncio.create_task(cleanup_loop())
    try:
        await idle()
    finally:
        cleanup_task.cancel()
        await app.stop()


if __name__ == "__main__":
    app.run(main())
