from pyrogram import Client, filters
from pyrogram.types import Message
from config import OWNER_ID
from utils.permissions import is_owner, is_authorized
from services.security_service import log_command, get_audit_summary, get_login_history_text, check_emergency_mode
from utils.logger import logger


@Client.on_message(filters.command("security"))
async def security_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    await log_command(message.from_user.id, "/security", message.chat.id)

    emergency = await check_emergency_mode()
    audit = await get_audit_summary(10)

    text = (
        "🛡️ **Security Dashboard**\n\n"
        f"Emergency Mode: {'🔴 ON' if emergency else '🟢 OFF'}\n\n"
        f"{audit}"
    )
    await message.reply(text)


@Client.on_message(filters.command("loginhistory"))
async def login_history(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    user_id = message.from_user.id
    if len(message.command) > 1:
        try:
            user_id = int(message.command[1])
        except ValueError:
            pass

    history = await get_login_history_text(user_id)
    await message.reply(history)
