from pyrogram import Client, filters
from pyrogram.types import Message
from utils.permissions import is_authorized
from services.translation_service import set_language, get_supported_languages, TRANSLATIONS
from utils.logger import logger


async def set_lang(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        langs = ", ".join(TRANSLATIONS.keys())
        await message.reply(f"Usage: /setlang <code>\nSupported: {langs}")
        return

    lang = message.command[1].lower()
    success = await set_language(message.chat.id, lang)
    if success:
        logger.info(f"Language set to {lang} in {message.chat.id}")
        await message.reply(f"🌍 Language set to `{lang}`.")
    else:
        supported = ", ".join(await get_supported_languages())
        await message.reply(f"❌ Unsupported language. Supported: {supported}")


async def translate_cmd(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    await message.reply(
        "🌍 **Translation System**\n\n"
        "Use /setlang <code> to change group language.\n\n"
        "Supported languages: " + ", ".join(TRANSLATIONS.keys())
    )
