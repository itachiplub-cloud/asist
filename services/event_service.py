import random
import time

from pyrogram import Client
from config import OWNER_ID
from database import Database
from utils.logger import logger

db = Database()


async def create_event(name: str, event_type: str, config: dict) -> dict:
    event = await db.create_event(name, event_type, config)
    logger.info(f"Event created: {name} ({event_type})")
    return event


async def delete_event(event_id) -> bool:
    success = await db.delete_event(event_id)
    if success:
        logger.info(f"Event {event_id} deleted")
    return success


async def list_events() -> str:
    events = await db.get_events()
    if not events:
        return "No events found."

    lines = "📜 **Events**\n\n"
    for e in events:
        eid = str(e.get("_id"))[-8:]
        name = e.get("name", "?")
        etype = e.get("type", "?")
        status = e.get("status", "?")
        lines += f"• `{eid}` | {name} [{etype}] - {status}\n"
    return lines


async def select_winner(participants: list) -> int:
    return random.choice(participants) if participants else None
