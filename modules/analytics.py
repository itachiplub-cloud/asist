import time

from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database
from utils.permissions import is_authorized
from utils.logger import logger

db = Database()


async def group_stats(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    chat_id = message.chat.id
    since_24h = time.time() - 86400
    since_7d = time.time() - 604800

    msg_24h = await db.get_message_count(chat_id, since_24h)
    msg_7d = await db.get_message_count(chat_id, since_7d)
    joins = await db.get_member_event_count(chat_id, "join", since_7d)
    leaves = await db.get_member_event_count(chat_id, "leave", since_7d)
    top = await db.get_top_users(chat_id, since_7d, 5)

    top_text = "\n".join([f"• `{u['_id']}` - {u['count']} msgs" for u in top]) or "N/A"

    text = (
        f"📊 **Group Statistics**\n\n"
        f"Messages (24h): {msg_24h}\n"
        f"Messages (7d): {msg_7d}\n"
        f"Joins (7d): {joins}\n"
        f"Leaves (7d): {leaves}\n"
        f"Growth (7d): +{joins - leaves}\n\n"
        f"**Top 5 Members:**\n{top_text}"
    )
    await message.reply(text)


async def activity_command(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    chat_id = message.chat.id
    since = time.time() - 604800
    hourly = await db.get_hourly_activity(chat_id, since)

    if not hourly:
        await message.reply("No activity data available.")
        return

    lines = "📈 **Activity (7d)**\n\n"
    for h in hourly:
        hour = h["_id"]
        count = h["count"]
        bar = "█" * min(count // 5 + 1, 20)
        lines += f"{hour:02d}:00 {bar} {count}\n"

    await message.reply(lines[:4000])


async def top_members(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    chat_id = message.chat.id
    since = time.time() - 604800
    top = await db.get_top_users(chat_id, since, 10)

    if not top:
        await message.reply("No data available.")
        return

    lines = "🏆 **Top 10 Members (7d)**\n\n"
    for i, u in enumerate(top, 1):
        lines += f"{i}. `{u['_id']}` - {u['count']} messages\n"

    await message.reply(lines)
