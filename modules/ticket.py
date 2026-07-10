from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database
from utils.permissions import is_authorized
from services.ticket_service import create_ticket, close_ticket, assign_ticket, get_tickets_summary
from utils.logger import logger

db = Database()


async def ticket_cmd(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /ticket <issue description>")
        return

    issue = " ".join(message.command[1:])
    priority = "normal"
    if "--high" in issue:
        priority = "high"
        issue = issue.replace("--high", "").strip()
    elif "--low" in issue:
        priority = "low"
        issue = issue.replace("--low", "").strip()

    ticket = await create_ticket(message.from_user.id, issue, priority)
    tid = str(ticket["_id"])[-8:]
    await message.reply(f"🎟️ Ticket `{tid}` created with priority {priority}.")


async def close_ticket_cmd(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /closeticket <ticket_id>")
        return

    from bson.objectid import ObjectId
    try:
        ticket_id = ObjectId(message.command[1])
    except Exception:
        await message.reply("❌ Invalid ticket ID.")
        return

    success = await close_ticket(ticket_id)
    await message.reply("✅ Ticket closed." if success else "❌ Ticket not found.")


async def tickets_cmd(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    status = message.command[1] if len(message.command) > 1 else None
    summary = await get_tickets_summary(status)
    await message.reply(summary)
