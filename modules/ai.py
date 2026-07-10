from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database
from utils.permissions import is_authorized
from services.ai_service import generate_rules, suggest_moderation
from services.translation_service import get_text
from utils.logger import logger

db = Database()


async def enable_ai(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply(await get_text(message.chat.id, "not_authorized"))
        return

    await db.set_ai_enabled(message.chat.id, True)
    logger.info(f"AI enabled in {message.chat.id} by {message.from_user.id}")
    await message.reply("🤖 **AI Group Manager enabled!**\n\nAuto FAQ, spam detection, and welcome messages are active.")


async def disable_ai(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply(await get_text(message.chat.id, "not_authorized"))
        return

    await db.set_ai_enabled(message.chat.id, False)
    logger.info(f"AI disabled in {message.chat.id} by {message.from_user.id}")
    await message.reply("🤖 **AI Group Manager disabled.**")


async def rules_command(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply(await get_text(message.chat.id, "not_authorized"))
        return

    rules = await generate_rules(message.chat.id)
    await message.reply(rules)


async def moderate_command(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply(await get_text(message.chat.id, "not_authorized"))
        return

    if len(message.command) < 3:
        await message.reply("Usage: /moderate <action> <user_id> <reason>")
        return

    action = message.command[1]
    try:
        user_id = int(message.command[2])
    except ValueError:
        await message.reply("❌ Invalid user ID.")
        return
    reason = " ".join(message.command[3:]) if len(message.command) > 3 else "No reason"

    suggestion = await suggest_moderation(action, user_id, reason)
    await message.reply(suggestion)
