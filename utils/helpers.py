import asyncio
import random
import time

from pyrogram.errors import FloodWait
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
    except Exception as e:
        error_str = str(e).lower()
        if "user is already a member" in error_str:
            return False, "already_member"
        if "privacy" in error_str or "cant_add_self" in error_str:
            return False, "privacy"
        if "user_id_invalid" in error_str or "user not found" in error_str:
            return False, "invalid_user"
        return False, error_str


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
