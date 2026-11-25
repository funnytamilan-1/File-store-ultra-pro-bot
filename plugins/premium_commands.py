from pyrogram import Client, filters
from database.admins import is_admin
from database.premium import add_premium, remove_premium
from database.logs import add_log


@Client.on_message(filters.command("addpremium") & filters.private)
async def add_premium_cmd(client, message):
    if not await is_admin(message.from_user.id):
        return
    try:
        user_id, days = int(message.command[1]), int(message.command[2])
        if days < 1:
            raise ValueError
    except (IndexError, ValueError):
        await message.reply_text("Usage: /addpremium user_id days (days must be positive)")
        return
    expiry = await add_premium(user_id, days)
    await add_log("add_premium", user_id=message.from_user.id, target_id=user_id, extra={"days": days})
    await message.reply_text(f"Premium enabled for {user_id} until {expiry:%Y-%m-%d %H:%M UTC}")


@Client.on_message(filters.command("delpremium") & filters.private)
async def del_premium_cmd(client, message):
    if not await is_admin(message.from_user.id):
        return
    try:
        user_id = int(message.command[1])
    except (IndexError, ValueError):
        await message.reply_text("Usage: /delpremium user_id")
        return
    removed = await remove_premium(user_id)
    await add_log("remove_premium", user_id=message.from_user.id, target_id=user_id)
    await message.reply_text("Premium removed." if removed else "No premium record found.")
