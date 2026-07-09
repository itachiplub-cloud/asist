from pyrogram import Client, filters
from pyrogram.types import Message
from utils.permissions import is_owner, is_authorized
from services.reward_service import add_reward, redeem_reward, list_rewards
from utils.logger import logger


@Client.on_message(filters.command("addreward"))
async def add_reward_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 4:
        await message.reply("Usage: /addreward <name> <points> <type>\nTypes: daily, invite, activity, premium")
        return

    name = message.command[1]
    try:
        points = int(message.command[2])
    except ValueError:
        await message.reply("❌ Invalid points.")
        return
    reward_type = message.command[3]

    await add_reward(name, points, reward_type)
    await message.reply(f"🎁 Reward `{name}` added ({points} pts, {reward_type}).")


@Client.on_message(filters.command("redeemreward"))
async def redeem_reward_cmd(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /redeemreward <reward_id>")
        return

    from bson.objectid import ObjectId
    try:
        reward_id = ObjectId(message.command[1])
    except Exception:
        await message.reply("❌ Invalid reward ID.")
        return

    result = await redeem_reward(message.from_user.id, reward_id)
    await message.reply(result)


@Client.on_message(filters.command("rewards"))
async def rewards_cmd(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    text = await list_rewards()
    await message.reply(text)
