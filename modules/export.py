from pyrogram import Client, filters
from pyrogram.types import Message
from utils.permissions import is_owner
from services.export_service import export_users, export_groups, export_logs, export_stats
from utils.logger import logger


@Client.on_message(filters.command("export"))
async def export_cmd(client: Client, message: Message):
    if not await is_owner(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply(
            "Usage: /export <type> [format]\n\n"
            "Types: users, groups, logs, stats\n"
            "Formats: json, csv (default: json)"
        )
        return

    export_type = message.command[1].lower()
    fmt = message.command[2].lower() if len(message.command) > 2 else "json"

    if fmt not in ("json", "csv"):
        await message.reply("❌ Invalid format. Use json or csv.")
        return

    exporters = {
        "users": export_users,
        "groups": export_groups,
        "logs": export_logs,
        "stats": export_stats,
    }

    exporter = exporters.get(export_type)
    if not exporter:
        await message.reply("❌ Invalid export type.")
        return

    msg = await message.reply(f"📁 Exporting {export_type}...")
    path = await exporter(fmt)
    if path:
        await msg.edit(f"✅ Exported to `{path}`")
        try:
            await client.send_document(message.chat.id, path)
        except Exception:
            pass
    else:
        await msg.edit("❌ Export failed.")
