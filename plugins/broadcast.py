from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from database.users import get_all_users
from database.admins import is_admin
from database.logs import add_log
import asyncio


@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_handler(client, message):
    if not await is_admin(message.from_user.id):
        return
    if not message.reply_to_message and len(message.command) < 2:
        await message.reply_text("Reply to a message or use /broadcast your message")
        return
    status = await message.reply_text("Broadcast started…")
    sent = failed = 0
    cursor = await get_all_users()
    async for user in cursor:
        user_id = user.get("user_id")
        if not user_id:
            continue
        try:
            if message.reply_to_message:
                await message.reply_to_message.copy(chat_id=user_id)
            else:
                await client.send_message(user_id, message.text.split(None, 1)[1])
            sent += 1
        except FloodWait as exc:
            await asyncio.sleep(exc.value)
            try:
                if message.reply_to_message:
                    await message.reply_to_message.copy(chat_id=user_id)
                else:
                    await client.send_message(user_id, message.text.split(None, 1)[1])
                sent += 1
            except Exception:
                failed += 1
        except Exception:
            failed += 1
    await add_log("broadcast", user_id=message.from_user.id, extra={"sent": sent, "failed": failed})
    await status.edit_text(f"Broadcast complete. Delivered: {sent}; failed: {failed}.")
