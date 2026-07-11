from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database
from utils.permissions import is_authorized
from utils.logger import logger

db = Database()


async def blacklist_user(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /blacklist <user_id>")
        return

    try:
        user_id = int(message.command[1])
    except ValueError:
        await message.reply("❌ Invalid user ID.")
        return

    reason = " ".join(message.command[2:]) if len(message.command) > 2 else None
    success = await db.blacklist_user(user_id, reason)
    if success:
        logger.info(f"User {user_id} blacklisted by {message.from_user.id}")
        await message.reply(f"✅ User `{user_id}` blacklisted successfully.")
    else:
        await message.reply(f"❌ User `{user_id}` is already blacklisted.")


async def unblacklist_user(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /unblacklist <user_id>")
        return

    try:
        user_id = int(message.command[1])
    except ValueError:
        await message.reply("❌ Invalid user ID.")
        return

    success = await db.unblacklist_user(user_id)
    if success:
        logger.info(f"User {user_id} unblacklisted by {message.from_user.id}")
        await message.reply(f"✅ User `{user_id}` removed from blacklist.")
    else:
        await message.reply(f"❌ User `{user_id}` is not in the blacklist.")
