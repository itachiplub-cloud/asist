from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database
from utils.permissions import is_owner, is_authorized
from services.notification_service import notify_owner
from utils.logger import logger

db = Database()


async def notify_settings(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ Only the owner can configure notifications.")
        return

    if len(message.command) < 3:
        await message.reply(
            "Usage: /notify <setting> <on|off>\n\n"
            "Settings: kick, floodwait, errors, invite_done, settings_change"
        )
        return

    setting = message.command[1].lower()
    value = message.command[2].lower() == "on"

    valid_settings = {"kick", "floodwait", "errors", "invite_done", "settings_change"}
    if setting not in valid_settings:
        await message.reply(f"❌ Invalid setting. Choose from: {', '.join(valid_settings)}")
        return

    await db.update_notify_setting(message.chat.id, setting, value)
    logger.info(f"Notification {setting} set to {value} by {message.from_user.id}")
    await message.reply(f"✅ Notification `{setting}` set to {'ON' if value else 'OFF'}.")


async def list_notifications(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ Only the owner can view notification settings.")
        return

    settings = await db.get_notify_settings(message.chat.id)
    lines = "🔔 **Notification Settings**\n\n"
    for key, val in settings.items():
        if key == "chat_id":
            continue
        icon = "✅" if val else "❌"
        lines += f"{icon} {key}: {'ON' if val else 'OFF'}\n"

    await message.reply(lines)
