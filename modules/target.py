from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database
from utils.permissions import is_owner, is_authorized
from utils.logger import logger

db = Database()


@Client.on_message(filters.command("settarget"))
async def set_target(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /settarget <chat_id>")
        return

    try:
        chat_id = int(message.command[1])
    except ValueError:
        await message.reply("❌ Invalid chat ID.")
        return

    try:
        chat = await client.get_chat(chat_id)
        title = chat.title or chat.username or str(chat_id)
    except Exception:
        title = str(chat_id)

    await db.set_target(chat_id, title)
    logger.info(f"Target group set to {chat_id} ({title}) by {message.from_user.id}")
    await message.reply(f"✅ Target group set to `{chat_id}` ({title}).")


@Client.on_message(filters.command("target"))
async def target_info(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    target = await db.get_target()
    if not target:
        await message.reply("❌ No target group has been set.")
        return

    text = (
        "🎯 **Target Group**\n"
        f"Chat ID: `{target['chat_id']}`\n"
        f"Title: {target.get('title', 'N/A')}"
    )
    await message.reply(text)
