from pyrogram import Client, filters
from pyrogram.types import Message
from database import Database
from utils.permissions import is_owner
from services.plugin_service import (
    discover_plugins, load_plugin, unload_plugin,
    reload_plugin, list_loaded_plugins,
)
from utils.logger import logger

db = Database()


async def load_plugin_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /load <plugin_name>")
        return

    name = message.command[1]
    success = load_plugin(name)
    if success:
        await message.reply(f"✅ Plugin `{name}` loaded.")
    else:
        await message.reply(f"❌ Failed to load plugin `{name}`.")


async def unload_plugin_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /unload <plugin_name>")
        return

    name = message.command[1]
    success = unload_plugin(name)
    if success:
        await message.reply(f"✅ Plugin `{name}` unloaded.")
    else:
        await message.reply(f"❌ Failed to unload plugin `{name}`.")


async def reload_plugin_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /reload <plugin_name>")
        return

    name = message.command[1]
    success = reload_plugin(name)
    if success:
        await message.reply(f"✅ Plugin `{name}` reloaded.")
    else:
        await message.reply(f"❌ Failed to reload plugin `{name}`.")


async def list_plugins(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    available = discover_plugins()
    loaded = list_loaded_plugins()

    text = "📦 **Plugin Marketplace**\n\n"
    text += "**Loaded:**\n"
    if loaded:
        text += "\n".join(f"• ✅ `{p}`" for p in loaded)
    else:
        text += "• None"

    text += "\n\n**Available:**\n"
    if available:
        text += "\n".join(f"• `{p}`" for p in available if p not in loaded)
    else:
        text += "• No plugins found"

    await message.reply(text)
