from pyrogram import Client
from database.settings import get_settings


@Client.on_chat_join_request()
async def auto_approve(client, request):
    settings = await get_settings()
    if not settings.get("force_join_request"):
        return
    allowed = set(settings.get("force_channels") or [])
    legacy = settings.get("force_channel")
    if legacy:
        allowed.add(legacy)
    chat = request.chat
    usernames = {chat.username, f"@{chat.username}"} if chat.username else set()
    if chat.id in allowed or usernames.intersection(allowed):
        await request.approve()
