import asyncio

from pyrogram.errors import FloodWait
from database import Database
from utils.logger import logger
from utils.session_manager import start_session, stop_session, running_session_count, get_session

db = Database()
_assistant_meta: dict = {}
_current_index = 0
_cooldown_managers: dict = {}


async def initialize_assistants():
    """Load assistant metadata only — do NOT start any sessions on boot."""
    assistants = await db.get_active_assistants()
    for a in assistants:
        aid = str(a["_id"])
        _assistant_meta[aid] = {
            "name": a.get("name", "Unnamed"),
            "session_string": a["session_string"],
        }
        logger.info(f"Loaded assistant metadata: {a.get('name', aid)} ({aid})")

    count = len(_assistant_meta)
    logger.info(f"Assistant metadata loaded: {count} assistant(s) registered")
    return list(_assistant_meta.keys())


async def get_next_assistant():
    """Lazily get the next available assistant, starting a session if needed."""
    global _current_index
    ids = list(_assistant_meta.keys())
    if not ids:
        logger.warning("No assistants registered")
        return None

    for _ in range(len(ids)):
        _current_index = (_current_index + 1) % len(ids)
        aid = ids[_current_index]
        meta = _assistant_meta[aid]
        session_string = meta["session_string"]

        existing = get_session(session_string)
        if existing and existing.is_connected:
            return existing

        logger.info(f"Lazy-starting assistant session: {meta['name']} ({aid})")
        client = await start_session(session_string, name=meta["name"])
        if client:
            return client

    logger.error("All assistants failed to start")
    return None


async def distribute_task(task_type: str, task_data: dict):
    client = await get_next_assistant()
    if not client:
        logger.warning("No assistant available for task distribution")
        return None
    logger.info(f"Distributed {task_type} task to assistant")
    return client


async def add_assistant_client(session_string: str, name: str = None):
    doc = await db.add_assistant(session_string, name)
    aid = str(doc["_id"])
    _assistant_meta[aid] = {
        "name": name or "Unnamed",
        "session_string": session_string,
    }
    logger.info(f"New assistant metadata saved: {name or aid} ({aid})")
    return doc, True


async def remove_assistant_client(assistant_id):
    aid = str(assistant_id)
    meta = _assistant_meta.pop(aid, None)
    if meta:
        await stop_session(meta["session_string"])
        logger.info(f"Stopped and removed assistant session: {meta.get('name', aid)}")
    await db.remove_assistant(assistant_id)
    logger.info(f"Assistant {assistant_id} removed from database")


async def get_assistant_stats() -> str:
    if not _assistant_meta:
        meta_count = len(_assistant_meta)
        db_count = len(await db.get_assistants())
        if db_count > 0:
            return "No assistants loaded. They will start on first use."
        return "No assistants configured."

    lines = "👥 **Assistants**\n\n"
    for aid, meta in _assistant_meta.items():
        client = get_session(meta["session_string"])
        online = "✅ Online" if client and client.is_connected else "❌ Offline"
        lines += f"• {meta['name']} — {online}\n"

    lines += f"\nActive sessions: {running_session_count()}"
    return lines
