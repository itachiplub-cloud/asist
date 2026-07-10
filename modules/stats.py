from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database
from utils.permissions import is_authorized
from utils.logger import logger

db = Database()


async def ping_command(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    import time
    start = time.time()
    ms = await message.reply("🏓 Pong!")
    end = time.time()
    latency = round((end - start) * 1000, 2)
    await ms.edit_text(f"🏓 **Pong!** `{latency}ms`")


async def stats_command(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    target = await db.get_target()
    sudo_users = await db.get_sudo_users()
    blacklist_count = await db.get_blacklist_count()
    total_invited = await db.get_total_invited()

    text = (
        "📊 **Bot Statistics**\n\n"
        f"Target Groups : {1 if target else 0}\n"
        f"Sudo Admins : {len(sudo_users)}\n"
        f"Blacklisted Users : {blacklist_count}\n"
        f"Total Invited : {total_invited}"
    )
    await message.reply(text)
