from pyrogram import Client
from config import OWNER_ID
from database import Database
from utils.logger import logger

db = Database()


async def notify_owner(client: Client, text: str) -> None:
    try:
        await client.send_message(OWNER_ID, text)
    except Exception as e:
        logger.error(f"Failed to notify owner: {e}")


async def notify_kicked(client: Client, chat_id: int, chat_title: str) -> None:
    logger.warning(f"Bot was kicked from {chat_title} ({chat_id})")
    await notify_owner(
        client,
        f"🚫 **Kicked from Group**\n\n"
        f"Bot was removed from `{chat_title}` (`{chat_id}`)."
    )


async def notify_floodwait(client: Client, seconds: int, source: str = None) -> None:
    source_text = f" in `{source}`" if source else ""
    await notify_owner(
        client,
        f"⚠️ **FloodWait Detected**{source_text}\n"
        f"Duration: {seconds}s"
    )


async def notify_error(client: Client, error: str, context: str = None) -> None:
    ctx = f" in `{context}`" if context else ""
    await notify_owner(
        client,
        f"❌ **Error Occurred**{ctx}\n`{error[:300]}`"
    )


async def notify_invite_done(client: Client, source: int, target: int, invited: int, skipped: int) -> None:
    await notify_owner(
        client,
        f"✅ **Invite Task Completed**\n\n"
        f"Source: `{source}`\n"
        f"Target: `{target}`\n"
        f"Invited: {invited}\n"
        f"Skipped: {skipped}"
    )


async def notify_settings_change(client: Client, chat_id: int, setting: str, value) -> None:
    await notify_owner(
        client,
        f"⚙️ **Settings Changed**\n"
        f"Chat: `{chat_id}`\n"
        f"`{setting}` → `{value}`"
    )


async def notify_session_invalid(client: Client) -> None:
    await notify_owner(
        client,
        "🔴 **Session Invalid!**\n"
        "The userbot session has expired or is invalid. "
        "Use /restartsession or update STRING_SESSION."
    )
