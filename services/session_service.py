import time
import asyncio

from pyrogram.errors import AccessTokenInvalid, AuthKeyUnregistered
from config import OWNER_ID
from database import Database
from utils import client_manager
from services.notification_service import notify_session_invalid, notify_owner
from utils.logger import logger

db = Database()
_health_check_task = None


async def check_session_health() -> dict:
    ub = client_manager.userbot
    health = {
        "last_check": time.time(),
        "is_valid": True,
        "me": None,
        "dc_id": None,
    }
    try:
        me = await ub.get_me()
        health["me"] = me.id if me else None
        health["dc_id"] = me.dc_id if hasattr(me, "dc_id") else None
    except (AuthKeyUnregistered, AccessTokenInvalid):
        health["is_valid"] = False
        logger.error("Session is invalid or expired")
        await notify_session_invalid()
    except Exception as e:
        health["is_valid"] = False
        health["error"] = str(e)
        logger.error(f"Session health check failed: {e}")

    await db.save_session_health(health)
    return health


async def get_session_status() -> str:
    health = await db.get_session_health()
    if not health:
        health = await check_session_health()

    uptime = time.time() - health.get("last_check", time.time())
    status = "✅ Valid" if health.get("is_valid") else "❌ Invalid"
    return (
        f"🔄 **Session Status**\n\n"
        f"Status: {status}\n"
        f"User ID: `{health.get('me', 'N/A')}`\n"
        f"DC ID: `{health.get('dc_id', 'N/A')}`\n"
        f"Last Check: {uptime:.0f}s ago"
    )


async def restart_session() -> bool:
    ub = client_manager.userbot
    bot = client_manager.bot
    try:
        await ub.stop()
        await asyncio.sleep(2)
        await ub.start()
        logger.info("Session restarted successfully")
        await notify_owner("🔄 **Session Restarted**\nBot session was restarted successfully.")
        return True
    except Exception as e:
        logger.error(f"Session restart failed: {e}")
        await notify_owner(f"❌ **Session Restart Failed**\n`{e}`")
        return False


async def start_health_monitor(interval: int = 3600):
    global _health_check_task

    async def _monitor():
        while True:
            await asyncio.sleep(interval)
            try:
                await check_session_health()
            except Exception as e:
                logger.error(f"Health monitor error: {e}")

    _health_check_task = asyncio.create_task(_monitor())
