from pyrogram import Client, filters
from pyrogram.types import Message
from utils.permissions import is_authorized
from utils.logger import logger


@Client.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    logger.info(f"User {message.from_user.id} used /start")

    text = (
        "🤖 **Assistant Invite Bot**\n\n"
        "I manage member invitations between Telegram groups.\n\n"
        "**Commands:**\n"
        "• /help - Show detailed help menu\n"
        "• /ping - Check bot latency\n"
        "• /stats - Bot statistics\n\n"
        "Use /help to see all available commands."
    )
    await message.reply(text)
