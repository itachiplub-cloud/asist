from pyrogram import Client, filters
from pyrogram.types import Message
from utils.permissions import is_authorized
from services.campaign_service import create_campaign, get_campaign_stats, export_campaign, compare_campaigns
from database import Database
from utils.logger import logger

db = Database()


@Client.on_message(filters.command("createcampaign"))
async def create_campaign_cmd(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 3:
        await message.reply("Usage: /createcampaign <name> <source_chat_id>")
        return

    name = message.command[1]
    try:
        source_chat_id = int(message.command[2])
    except ValueError:
        await message.reply("❌ Invalid source chat ID.")
        return

    target = await db.get_target()
    if not target:
        await message.reply("❌ No target group set. Use /settarget first.")
        return

    await create_campaign(name, source_chat_id, target["chat_id"])
    logger.info(f"Campaign '{name}' created by {message.from_user.id}")
    await message.reply(f"✅ Campaign `{name}` created.")


@Client.on_message(filters.command("campaignstats"))
async def campaign_stats(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /campaignstats <name>")
        return

    stats = await get_campaign_stats(message.command[1])
    await message.reply(stats)


@Client.on_message(filters.command("deletecampaign"))
async def delete_campaign(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /deletecampaign <name>")
        return

    success = await db.delete_campaign(message.command[1])
    if success:
        await message.reply("✅ Campaign deleted.")
    else:
        await message.reply("❌ Campaign not found.")
