import time

from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database
from utils.permissions import is_owner
from services.scheduler_service import run_scheduler
from utils.logger import logger

db = Database()


async def schedule_task(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 3:
        await message.reply(
            "Usage: /schedule <type> <interval_seconds> [config_json]\n\n"
            "Types: broadcast, backup, invite, report\n"
            "Example: /schedule report 86400"
        )
        return

    task_type = message.command[1].lower()
    try:
        interval = int(message.command[2])
    except ValueError:
        await message.reply("❌ Invalid interval.")
        return

    config = {}
    if len(message.command) > 3:
        import json
        try:
            config = json.loads(" ".join(message.command[3:]))
        except json.JSONDecodeError:
            await message.reply("❌ Invalid JSON config.")
            return

    task = {
        "type": task_type,
        "interval": interval,
        "config": config,
        "scheduled_at": time.time(),
        "created_at": time.time(),
    }
    await db.create_scheduled_task(task)
    logger.info(f"Scheduled task created: {task_type} every {interval}s")
    await message.reply(f"✅ Scheduled `{task_type}` task every {interval}s.")


async def list_schedules(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    tasks = await db.get_scheduled_tasks()
    if not tasks:
        await message.reply("No scheduled tasks.")
        return

    lines = "🗓️ **Scheduled Tasks**\n\n"
    for t in tasks:
        tid = str(t["_id"])[-8:]
        lines += f"• `{tid}` | {t['type']} | every {t['interval']}s\n"
    await message.reply(lines)


async def cancel_schedule(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /cancelschedule <task_id>")
        return

    from bson.objectid import ObjectId
    try:
        task_id = ObjectId(message.command[1])
    except Exception:
        await message.reply("❌ Invalid task ID.")
        return

    success = await db.delete_scheduled_task(task_id)
    if success:
        await message.reply("✅ Task cancelled.")
    else:
        await message.reply("❌ Task not found.")
