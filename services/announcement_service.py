import time

from pyrogram import Client
from database import Database
from utils.logger import logger

db = Database()


async def send_announcement(client: Client, text: str, chats: list[int],
                            media: str = None, buttons: list = None,
                            pin: bool = False) -> dict:
    result = {"sent": 0, "failed": 0}
    for chat_id in chats:
        try:
            if media:
                msg = await client.send_photo(chat_id, media, caption=text)
            else:
                msg = await client.send_message(chat_id, text)

            if pin:
                try:
                    await client.pin_chat_message(chat_id, msg.id)
                except Exception:
                    pass

            result["sent"] += 1
        except Exception as e:
            logger.warning(f"Announcement to {chat_id} failed: {e}")
            result["failed"] += 1

        await db.save_announcement(chat_id, text, media, buttons)
        await asyncio.sleep(1)

    return result


async def get_all_group_chats(client: Client) -> list[int]:
    chats = []
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ("group", "supergroup"):
            chats.append(dialog.chat.id)
    return chats


import asyncio
