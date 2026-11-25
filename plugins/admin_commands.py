from pyrogram import Client, filters
from config import OWNER_ID
from database.admins import add_admin, remove_admin
from database.logs import add_log


@Client.on_message(filters.command("addadmin") & filters.private)
async def add_admin_cmd(client, message):
    if message.from_user.id != OWNER_ID:
        return
    try:
        new_admin = int(message.command[1])
    except (IndexError, ValueError):
        await message.reply_text("Usage: /addadmin user_id")
        return
    await add_admin(new_admin)
    await add_log("add_admin", user_id=message.from_user.id, target_id=new_admin)
    await message.reply_text("Admin added.")


@Client.on_message(filters.command("removeadmin") & filters.private)
async def remove_admin_cmd(client, message):
    if message.from_user.id != OWNER_ID:
        return
    try:
        admin_id = int(message.command[1])
    except (IndexError, ValueError):
        await message.reply_text("Usage: /removeadmin user_id")
        return
    if admin_id == OWNER_ID:
        await message.reply_text("The owner account cannot be removed.")
        return
    await remove_admin(admin_id)
    await add_log("remove_admin", user_id=message.from_user.id, target_id=admin_id)
    await message.reply_text("Admin removed.")
