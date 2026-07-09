import asyncio
import time

from pyrogram import Client
from database import Database
from utils.logger import logger

db = Database()
_scheduler_tasks: dict = {}

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


async def run_scheduler(client: Client):
    tasks = await db.get_scheduled_tasks()
    for t in tasks:
        task_id = str(t["_id"])
        if task_id not in _scheduler_tasks:
            _scheduler_tasks[task_id] = asyncio.create_task(
                _execute_task(client, t)
            )


async def _execute_task(client: Client, task: dict):
    task_id = str(task["_id"])
    interval = task.get("interval", 86400)
    task_type = task.get("type")
    config = task.get("config", {})

    while True:
        now = time.time()
        task_time = task.get("scheduled_at", now)

        sleep_seconds = task_time - now
        if sleep_seconds > 0:
            await asyncio.sleep(sleep_seconds)

        try:
            if task_type == "broadcast":
                text = config.get("text", "")
                chats = config.get("chats", [])
                for chat_id in chats:
                    try:
                        await client.send_message(chat_id, text)
                    except Exception as e:
                        logger.warning(f"Broadcast to {chat_id} failed: {e}")
                    await asyncio.sleep(1)

            elif task_type == "backup":
                from services.backup_service import run_backup
                await run_backup(client)

            elif task_type == "invite":
                from modules.invite import invite_start
                logger.info(f"Scheduled invite task: {config}")

            elif task_type == "report":
                from services.analytics_service import generate_daily_report
                await generate_daily_report(client)

            logger.info(f"Scheduled task {task_id} ({task_type}) executed")
        except Exception as e:
            logger.error(f"Scheduled task {task_id} failed: {e}")

        if interval <= 0:
            await db.delete_scheduled_task(task["_id"])
            break

        await db.scheduled_tasks.update_one(
            {"_id": task["_id"]},
            {"$set": {"scheduled_at": time.time() + interval}},
        )
        task["scheduled_at"] = time.time() + interval
        await asyncio.sleep(interval)


async def stop_scheduler():
    for tid, task in _scheduler_tasks.items():
        task.cancel()
    _scheduler_tasks.clear()
