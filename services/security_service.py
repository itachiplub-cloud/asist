import time
from datetime import datetime

from config import OWNER_ID, EMERGENCY_MODE
from database import Database
from utils.logger import logger

db = Database()


async def log_command(user_id: int, command: str, chat_id: int = None) -> None:
    await db.log_audit({
        "user_id": user_id,
        "command": command,
        "chat_id": chat_id,
        "action": "command",
        "timestamp": time.time(),
    })


async def log_dangerous_command(user_id: int, command: str, chat_id: int = None) -> None:
    await db.log_audit({
        "user_id": user_id,
        "command": command,
        "chat_id": chat_id,
        "action": "dangerous_command",
        "timestamp": time.time(),
    })


async def check_emergency_mode() -> bool:
    return EMERGENCY_MODE


async def require_owner_confirmation(user_id: int, command: str) -> bool:
    if user_id == OWNER_ID:
        await log_command(user_id, command)
        return True
    await log_dangerous_command(user_id, command)
    return False


async def get_audit_summary(limit: int = 50) -> str:
    logs = await db.get_audit_logs(limit)
    if not logs:
        return "No audit logs found."

    lines = "🛡️ **Recent Audit Logs**\n\n"
    for log in logs[:10]:
        ts = datetime.fromtimestamp(log.get("timestamp", 0)).strftime("%Y-%m-%d %H:%M")
        action = log.get("action", "unknown")
        uid = log.get("user_id", "?")
        cmd = log.get("command", "?")
        lines += f"• [{ts}] {uid}: {cmd} ({action})\n"
    return lines


async def get_login_history_text(user_id: int) -> str:
    history = await db.get_login_history(user_id)
    if not history:
        return "No login history found."

    lines = f"🔐 **Login History for `{user_id}`**\n\n"
    for h in history[:10]:
        ts = datetime.fromtimestamp(h.get("timestamp", 0)).strftime("%Y-%m-%d %H:%M")
        status = "✅ Success" if h.get("success") else "❌ Failed"
        device = h.get("device", "unknown")
        lines += f"• [{ts}] {status} ({device})\n"
    return lines
