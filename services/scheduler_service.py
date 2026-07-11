import asyncio
import time

from database import Database
from utils import client_manager
from utils.logger import logger

db = Database()
_scheduler_tasks: dict = {}


async def run_scheduler():
    tasks = await db.get_scheduled_tasks()
    for t in tasks:
        task_id = str(t["_id"])
        if task_id not in _scheduler_tasks:
            _scheduler_tasks[task_id] = asyncio.create_task(
                _execute_task(t)
            )


async def _execute_task(task: dict):
    task_id = str(task["_id"])
    interval = task.get("interval", 86400)
    task_type = task.get("type")
    config = task.get("config", {})

    ub = client_manager.userbot if task_type in ("broadcast", "invite") else None

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
                        from utils.helpers import validate_chat_id
                        if not await validate_chat_id(ub, chat_id):
                            logger.warning(f"Broadcast: invalid chat {chat_id}, skipping")
                            continue
                        await ub.send_message(chat_id, text)
                    except Exception as e:
                        logger.warning(f"Broadcast to {chat_id} failed: {e}")
                    await asyncio.sleep(1)

            elif task_type == "backup":
                from services.backup_service import run_backup
                await run_backup()

            elif task_type == "invite":
                logger.info(f"Scheduled invite task: {config}")

            elif task_type == "report":
                from services.analytics_service import generate_daily_report
                await generate_daily_report()

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
