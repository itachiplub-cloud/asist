from pyrogram.errors import PeerIdInvalid, ChannelInvalid, ChannelPrivate

from config import OWNER_ID
from utils import client_manager
from utils.logger import logger


async def notify_owner(text: str) -> None:
    try:
        await client_manager.bot.send_message(OWNER_ID, text)
    except (PeerIdInvalid, ChannelInvalid, ChannelPrivate) as e:
        logger.critical(f"OWNER_ID {OWNER_ID} is invalid or bot cannot reach it: {e}")
    except Exception as e:
        logger.error(f"Failed to notify owner: {e}")


async def notify_kicked(chat_id: int, chat_title: str) -> None:
    logger.warning(f"Bot was kicked from {chat_title} ({chat_id})")
    await notify_owner(
        f"🚫 **Kicked from Group**\n\n"
        f"Bot was removed from `{chat_title}` (`{chat_id}`)."
    )


async def notify_floodwait(seconds: int, source: str = None) -> None:
    source_text = f" in `{source}`" if source else ""
    await notify_owner(
        f"⚠️ **FloodWait Detected**{source_text}\n"
        f"Duration: {seconds}s"
    )


async def notify_error(error: str, context: str = None) -> None:
    ctx = f" in `{context}`" if context else ""
    await notify_owner(
        f"❌ **Error Occurred**{ctx}\n`{error[:300]}`"
    )


async def notify_invite_done(source: int, target: int, invited: int, skipped: int) -> None:
    await notify_owner(
        f"✅ **Invite Task Completed**\n\n"
        f"Source: `{source}`\n"
        f"Target: `{target}`\n"
        f"Invited: {invited}\n"
        f"Skipped: {skipped}"
    )


async def notify_settings_change(chat_id: int, setting: str, value) -> None:
    await notify_owner(
        f"⚙️ **Settings Changed**\n"
        f"Chat: `{chat_id}`\n"
        f"`{setting}` → `{value}`"
    )


async def notify_session_invalid() -> None:
    await notify_owner(
        "🔴 **Session Invalid!**\n"
        "The userbot session has expired or is invalid. "
        "Use /restartsession or update STRING_SESSION."
    )
