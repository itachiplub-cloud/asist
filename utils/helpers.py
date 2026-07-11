import asyncio
import random
import time

from pyrogram.errors import FloodWait, PeerIdInvalid, ChannelInvalid, ChannelPrivate
from utils.logger import logger


async def safe_invite(client, chat_id, user_id):
    try:
        await client.add_chat_members(chat_id, user_id)
        return True, None
    except FloodWait as e:
        logger.warning(f"FloodWait for {e.value}s on user {user_id}")
        if e.value > 3600:
            return False, "flood_exceeded"
        await asyncio.sleep(e.value + 10)
        return False, "flood_handled"
    except (PeerIdInvalid, ChannelInvalid, ChannelPrivate) as e:
        logger.warning(f"Invalid peer {chat_id}: {e}")
        return False, f"invalid_peer:{chat_id}"
    except Exception as e:
        error_str = str(e).lower()
        if "user is already a member" in error_str:
            return False, "already_member"
        if "privacy" in error_str or "cant_add_self" in error_str:
            return False, "privacy"
        if "user_id_invalid" in error_str or "user not found" in error_str:
            return False, "invalid_user"
        return False, error_str


async def validate_chat_id(client, chat_id: int) -> bool:
    """Check if a chat ID is accessible. Returns True if valid."""
    try:
        chat = await client.get_chat(chat_id)
        logger.info(f"Validated group {chat_id}: {chat.title or 'no title'}")
        return True
    except (PeerIdInvalid, ChannelInvalid, ChannelPrivate) as e:
        logger.warning(f"Invalid group {chat_id}: {e}")
        return False
    except FloodWait as e:
        wait = e.value + 5
        logger.warning(f"FloodWait validating group {chat_id}: sleeping {wait}s")
        await asyncio.sleep(wait)
        return await validate_chat_id(client, chat_id)
    except Exception as e:
        logger.warning(f"Could not validate group {chat_id}: {e}")
        return False


def get_cooldown():
    from config import COOLDOWN_MIN, COOLDOWN_MAX
    return random.randint(COOLDOWN_MIN, COOLDOWN_MAX)


def format_duration(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)
