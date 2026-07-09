from pyrogram import Client, filters
from pyrogram.types import Message
from utils.permissions import is_owner
from services.monitor_service import get_system_info
from utils.logger import logger


@Client.on_message(filters.command("system"))
async def system_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    info = await get_system_info()

    import time
    from services.monitor_service import get_uptime

    text = (
        f"{info}\n"
        f"🤖 **Bot Info**\n"
        f"User: `{client.me.id}`\n"
        f"DC: `{client.me.dc_id}`\n"
    )
    await message.reply(text)
