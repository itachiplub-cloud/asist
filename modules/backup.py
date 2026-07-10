import os

from pyrogram import Client, filters
from pyrogram.types import Message
from utils.permissions import is_owner
from services.backup_service import run_backup, restore_backup, toggle_autobackup, get_backup_list
from utils.logger import logger


@Client.on_message(filters.command("backup"))
async def backup_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    msg = await message.reply("💾 Creating backup...")
    path = await run_backup()
    await msg.edit(f"✅ Backup created: `{path}`")


@Client.on_message(filters.command("restore"))
async def restore_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        backups = await get_backup_list()
        if not backups:
            await message.reply("No backups found.")
            return
        text = "📋 **Available Backups**\n\n" + "\n".join(f"• `{b}`" for b in backups[:10])
        await message.reply(text + "\n\nUsage: /restore <filename>")
        return

    backup_path = os.path.join("backups", message.command[1])
    msg = await message.reply("🔄 Restoring from backup...")
    success = await restore_backup(backup_path)
    await msg.edit("✅ Restore completed." if success else "❌ Restore failed.")


@Client.on_message(filters.command("autobackup"))
async def auto_backup(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /autobackup <on|off> [interval_hours]")
        return

    enabled = message.command[1].lower() == "on"
    interval = int(message.command[2]) if len(message.command) > 2 else 24

    setting = await toggle_autobackup(enabled, interval)
    status = "ON" if enabled else "OFF"
    await message.reply(f"💾 Auto backup set to {status} (every {interval}h).")
