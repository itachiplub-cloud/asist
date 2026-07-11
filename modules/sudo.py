from pyrogram import Client, filters
from pyrogram.types import Message
from config import OWNER_ID
from database import Database
from utils.permissions import is_owner
from utils.logger import logger

db = Database()


async def add_sudo(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /addsudo <user_id>")
        return

    try:
        user_id = int(message.command[1])
    except ValueError:
        await message.reply("❌ Invalid user ID.")
        return

    if user_id == OWNER_ID:
        await message.reply("❌ The owner is already a super admin.")
        return

    success = await db.add_sudo(user_id)
    if success:
        logger.info(f"Owner {message.from_user.id} added sudo {user_id}")
        await message.reply(f"✅ Sudo admin `{user_id}` added successfully.")
    else:
        await message.reply(f"❌ User `{user_id}` is already a sudo admin.")


async def del_sudo(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /delsudo <user_id>")
        return

    try:
        user_id = int(message.command[1])
    except ValueError:
        await message.reply("❌ Invalid user ID.")
        return

    success = await db.remove_sudo(user_id)
    if success:
        logger.info(f"Owner {message.from_user.id} removed sudo {user_id}")
        await message.reply(f"✅ Sudo admin `{user_id}` removed successfully.")
    else:
        await message.reply(f"❌ User `{user_id}` is not a sudo admin.")


async def sudo_list(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    sudo_users = await db.get_sudo_users()
    if not sudo_users:
        await message.reply("👑 No sudo admins have been added yet.")
        return

    lines = "👑 **Sudo Admins**\n"
    for uid in sudo_users:
        lines += f"• `{uid}`\n"

    await message.reply(lines)
