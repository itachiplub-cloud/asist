import random

from pyrogram import Client
from config import API_ID, API_HASH
from database import Database
from utils.logger import logger

db = Database()
_clients: dict = {}
_current_index = 0
_cooldown_managers: dict = {}


async def initialize_assistants():
    assistants = await db.get_active_assistants()
    for a in assistants:
        aid = str(a["_id"])
        if aid not in _clients:
            try:
                client = Client(
                    name=f"assistant_{aid}",
                    api_id=API_ID,
                    api_hash=API_HASH,
                    session_string=a["session_string"],
                    in_memory=True,
                )
                await client.start()
                _clients[aid] = client
                logger.info(f"Assistant {a.get('name', aid)} started")
            except Exception as e:
                logger.error(f"Failed to start assistant {aid}: {e}")

    return list(_clients.keys())


async def get_next_assistant():
    global _current_index
    ids = list(_clients.keys())
    if not ids:
        return None
    _current_index = (_current_index + 1) % len(ids)
    return _clients[ids[_current_index]]


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
    try:
        client = Client(
            name=f"assistant_{aid}",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session_string,
            in_memory=True,
        )
        await client.start()
        _clients[aid] = client
        logger.info(f"New assistant {name or aid} started")
        return doc, True
    except Exception as e:
        logger.error(f"Failed to start new assistant: {e}")
        return doc, False


async def remove_assistant_client(assistant_id):
    aid = str(assistant_id)
    if aid in _clients:
        try:
            await _clients[aid].stop()
        except Exception:
            pass
        del _clients[aid]
    await db.remove_assistant(assistant_id)
    logger.info(f"Assistant {assistant_id} removed")


async def get_assistant_stats() -> str:
    assistants = await db.get_assistants()
    if not assistants:
        return "No assistants configured."

    lines = "👥 **Assistants**\n\n"
    for a in assistants:
        aid = str(a["_id"])
        online = "✅ Online" if aid in _clients else "❌ Offline"
        lines += (
            f"• {a.get('name', 'Unnamed')}\n"
        )
    return lines
