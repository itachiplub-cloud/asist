from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database
from utils.permissions import is_authorized
from utils.logger import logger

db = Database()


@Client.on_message(filters.command("invitestatus"))
async def invite_status(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    from modules.invite import invite_running

    progress = await db.get_progress()
    if not progress:
        await message.reply("❌ No invite process is running or saved.")
        return

    running = invite_running.get(progress.get("source_chat_id"), False)
    text = (
        "📊 **Invite Status**\n\n"
        f"Source Group : `{progress.get('source_chat_id', 'N/A')}`\n"
        f"Target Group : `{progress.get('target_chat_id', 'N/A')}`\n"
        f"Invited : {progress.get('invited_count', 0)}\n"
        f"Skipped : {progress.get('skipped_count', 0)}\n"
        f"Errors : {progress.get('error_count', 0)}\n"
        f"Running : {'Yes' if running else 'No'}"
    )
    await message.reply(text)
