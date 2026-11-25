import asyncio
from pyrogram import Client, filters
from database.admins import is_admin, count_admins
from database.users import count_users
from database.files import count_files
from database.premium import count_premium_users
from database.logs import count_logs


@Client.on_message(filters.command("stats") & filters.private)
async def stats_handler(client, message):
    if not await is_admin(message.from_user.id):
        await message.reply_text("🚫 You are not authorized to use this command.")
        return
    users, files, admins, premium, logs = await asyncio.gather(
        count_users(), count_files(), count_admins(), count_premium_users(), count_logs()
    )
    await message.reply_text(
        "📊 **Bot Statistics**\n\n"
        f"👥 Users: {users}\n📂 Files: {files}\n🛡 Admins: {admins}\n"
        f"💎 Active premium: {premium}\n📝 Logs: {logs}"
    )
