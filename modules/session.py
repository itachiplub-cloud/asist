from pyrogram import Client, filters
from pyrogram.types import Message
from utils.permissions import is_owner
from services.session_service import get_session_status, restart_session
from utils.logger import logger


@Client.on_message(filters.command("sessionstatus"))
async def session_status(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    status = await get_session_status(client)
    await message.reply(status)


@Client.on_message(filters.command("restartsession"))
async def restart_session_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    msg = await message.reply("🔄 Restarting session...")
    success = await restart_session(client)
    if success:
        await msg.edit("✅ Session restarted successfully.")
    else:
        await msg.edit("❌ Session restart failed. Check logs.")
