from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database
from utils.permissions import is_owner
from services.cluster_service import add_assistant_client, remove_assistant_client, get_assistant_stats
from utils.logger import logger

db = Database()


async def add_assistant(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /addassistant <session_string> [name]")
        return

    session_string = message.command[1]
    name = " ".join(message.command[2:]) if len(message.command) > 2 else None

    doc, success = await add_assistant_client(session_string, name)
    if success:
        await message.reply(f"✅ Assistant `{name or doc.get('name')}` added and connected.")
    else:
        await message.reply(f"⚠️ Assistant added to DB but failed to connect. Check session string.")


async def remove_assistant(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /removeassistant <assistant_id>")
        return

    from bson.objectid import ObjectId
    try:
        assistant_id = ObjectId(message.command[1])
    except Exception:
        await message.reply("❌ Invalid assistant ID.")
        return

    await remove_assistant_client(assistant_id)
    await message.reply("✅ Assistant removed.")


async def list_assistants(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    stats = await get_assistant_stats()
    await message.reply(stats)
