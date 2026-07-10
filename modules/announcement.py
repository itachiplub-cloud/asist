from pyrogram import Client, filters
from pyrogram.types import Message
from utils import client_manager
from utils.permissions import is_owner
from services.announcement_service import send_announcement, get_all_group_chats
from utils.logger import logger


@Client.on_message(filters.command("announce"))
async def announce_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /announce <text>")
        return

    ub = client_manager.userbot
    text = " ".join(message.command[1:])
    chats = await get_all_group_chats(ub)

    msg = await message.reply(f"📢 Sending announcement to {len(chats)} groups...")
    result = await send_announcement(ub, text, chats)
    await msg.edit(f"✅ Sent: {result['sent']} | Failed: {result['failed']}")


@Client.on_message(filters.command("pinannounce"))
async def pin_announce(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /pinannounce <text>")
        return

    ub = client_manager.userbot
    text = " ".join(message.command[1:])
    chats = await get_all_group_chats(ub)

    msg = await message.reply(f"📌 Pinning announcement to {len(chats)} groups...")
    result = await send_announcement(ub, text, chats, pin=True)
    await msg.edit(f"✅ Pinned: {result['sent']} | Failed: {result['failed']}")
