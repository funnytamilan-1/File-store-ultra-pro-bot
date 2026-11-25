from datetime import datetime, timedelta, timezone
from pyrogram import Client, filters
from config import WEB_URL, AUTO_DELETE_HOURS
from database.files import save_file
from database.logs import add_log
from database.shortlinks import create_shortlink
from middleware.rate_limit import check_rate_limit
from middleware.force_sub import check_force
from utils.link_generator import generate_secure_link


@Client.on_message((filters.document | filters.video | filters.audio) & filters.private)
async def store_file(client, message):
    if not message.from_user:
        return
    if not await check_rate_limit(message.from_user.id):
        await message.reply_text("Please wait a few seconds before uploading another file.")
        return
    if not await check_force(client, message.from_user.id):
        await message.reply_text("Please join the required channels before uploading files.")
        return
    file = message.document or message.video or message.audio
    file_name = getattr(file, "file_name", None) or f"telegram_{file.file_unique_id}"
    expires_at = datetime.now(timezone.utc) + timedelta(hours=AUTO_DELETE_HOURS) if AUTO_DELETE_HOURS else None
    await save_file(file.file_id, file_name, message.from_user.id, type(file).__name__, getattr(file, "file_size", 0), expires_at)
    await add_log("file_upload", user_id=message.from_user.id, extra={"file_name": file_name, "auto_delete_hours": AUTO_DELETE_HOURS})
    signed = generate_secure_link(file.file_id, expiry_seconds=86400)
    destination = f"{WEB_URL}/file/{signed}"
    short = await create_shortlink(destination, message.from_user.id)
    link = f"{WEB_URL}/s/{short['slug']}"
    expiry_note = f"The file record expires after {AUTO_DELETE_HOURS} hours." if AUTO_DELETE_HOURS else "The link expires in 24 hours."
    await message.reply_text(f"✅ File saved. {expiry_note}\nShort link: {link}", disable_web_page_preview=True)
