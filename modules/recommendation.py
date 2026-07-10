from pyrogram import Client, filters
from pyrogram.types import Message
from utils.permissions import is_owner
from services.recommendation_service import get_recommendations
from utils.logger import logger


async def recommend_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    msg = await message.reply("🧠 Generating recommendations...")
    recommendations = await get_recommendations()
    await msg.edit(recommendations)
