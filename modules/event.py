from pyrogram import Client, filters
from pyrogram.types import Message
from utils.permissions import is_owner
from services.event_service import create_event, delete_event, list_events
from utils.logger import logger


@Client.on_message(filters.command("createevent"))
async def create_event_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 3:
        await message.reply("Usage: /createevent <name> <type>\nTypes: campaign, announcement, competition")
        return

    name = message.command[1]
    event_type = message.command[2].lower()

    config = {}
    if len(message.command) > 3:
        import json
        try:
            config = json.loads(" ".join(message.command[3:]))
        except json.JSONDecodeError:
            pass

    await create_event(name, event_type, config)
    await message.reply(f"📜 Event `{name}` created ({event_type}).")


@Client.on_message(filters.command("events"))
async def events_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    text = await list_events()
    await message.reply(text)


@Client.on_message(filters.command("deleteevent"))
async def delete_event_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /deleteevent <event_id>")
        return

    from bson.objectid import ObjectId
    try:
        event_id = ObjectId(message.command[1])
    except Exception:
        await message.reply("❌ Invalid event ID.")
        return

    success = await delete_event(event_id)
    await message.reply("✅ Event deleted." if success else "❌ Event not found.")
