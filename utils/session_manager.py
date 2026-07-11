import asyncio
from pyrogram import Client
from pyrogram.errors import FloodWait
from config import API_ID, API_HASH
from utils.logger import logger

_running_clients: dict = {}


async def start_session(session_string: str, name: str = "session") -> Client | None:
    if session_string in _running_clients:
        client = _running_clients[session_string]
        if client.is_connected:
            logger.info(f"Session '{name}' already running, reusing")
            return client
        _running_clients.pop(session_string, None)

    client = Client(
        name=f"session_{name}_{len(_running_clients)}",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=session_string,
        in_memory=True,
    )

    retries = 0
    while True:
        try:
            logger.info(f"Starting session '{name}'...")
            await client.start()
            _running_clients[session_string] = client
            logger.info(f"Session '{name}' started as {client.me.id}")
            return client
        except FloodWait as e:
            retries += 1
            wait = e.value + 5
            logger.warning(f"FloodWait starting session '{name}': {wait}s (retry {retries})")
            await asyncio.sleep(wait)
            if retries >= 5:
                logger.error(f"Gave up starting session '{name}' after {retries} FloodWait retries")
                return None


async def stop_session(session_string: str):
    client = _running_clients.pop(session_string, None)
    if client:
        try:
            await client.stop()
            logger.info(f"Session stopped")
        except Exception as e:
            logger.warning(f"Error stopping session: {e}")


async def stop_all_sessions():
    for sid in list(_running_clients.keys()):
        await stop_session(sid)


def running_session_count() -> int:
    return len(_running_clients)


def get_session(session_string: str) -> Client | None:
    return _running_clients.get(session_string)
