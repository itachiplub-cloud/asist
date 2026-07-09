from pyrogram import Client, filters
from pyrogram.types import Message
from utils.permissions import is_owner
from services.api_service import create_api_key, revoke_api_key, list_api_keys
from utils.logger import logger


@Client.on_message(filters.command("apikey"))
async def api_key_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /apikey <name> [permissions...]\nPermissions: read, write, admin\nExample: /apikey MyApp read write")
        return

    name = message.command[1]
    permissions = message.command[2:] if len(message.command) > 2 else ["read"]

    result = await create_api_key(name, permissions)
    key = result.get("key", "")
    await message.reply(
        f"🔑 **API Key Created**\n\n"
        f"Name: {name}\n"
        f"Key: `{key}`\n"
        f"Permissions: {', '.join(permissions)}\n\n"
        "⚠️ Save this key - it won't be shown again!"
    )


@Client.on_message(filters.command("revokeapikey"))
async def revoke_api_key_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /revokeapikey <key>")
        return

    key = message.command[1]
    success = await revoke_api_key(key)
    await message.reply("✅ API key revoked." if success else "❌ Key not found.")


@Client.on_message(filters.command("listapikeys"))
async def list_api_keys_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    text = await list_api_keys()
    await message.reply(text)
