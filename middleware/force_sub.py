from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, ChannelPrivate
from database.settings import get_settings


async def check_force(client, user_id: int) -> bool:
    settings = await get_settings()
    channels = list(settings.get("force_channels") or [])
    legacy_channel = settings.get("force_channel")
    if legacy_channel and legacy_channel not in channels:
        channels.append(legacy_channel)
    if not channels:
        return True

    allowed = {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
    for channel in channels:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status not in allowed:
                return False
        except (UserNotParticipant, PeerIdInvalid, ChannelPrivate):
            return False
        except Exception:
            return False
    return True
