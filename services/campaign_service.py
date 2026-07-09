import csv
import json
import os
from datetime import datetime

from config import EXPORT_DIR
from database import Database
from utils.logger import logger

db = Database()


async def create_campaign(name: str, source_chat_id: int, target_chat_id: int) -> dict:
    return await db.create_campaign(name, source_chat_id, target_chat_id)


async def get_campaign_stats(name: str) -> str:
    camp = await db.get_campaign(name)
    if not camp:
        return "❌ Campaign not found."

    return (
        f"📊 **Campaign: {camp['name']}**\n\n"
        f"Source: `{camp['source_chat_id']}`\n"
        f"Target: `{camp['target_chat_id']}`\n"
        f"Invited: {camp.get('invited', 0)}\n"
        f"Joined: {camp.get('joined', 0)}\n"
        f"Left: {camp.get('left', 0)}\n"
        f"Status: {camp.get('status', 'N/A')}"
    )


async def export_campaign(name: str, fmt: str = "json") -> str | None:
    camp = await db.get_campaign(name)
    if not camp:
        return None

    os.makedirs(EXPORT_DIR, exist_ok=True)
    filename = f"{EXPORT_DIR}/campaign_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{fmt}"

    if fmt == "json":
        with open(filename, "w") as f:
            json.dump(camp, f, indent=2, default=str)
    elif fmt == "csv":
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(camp.keys())
            writer.writerow(camp.values())

    logger.info(f"Campaign {name} exported to {filename}")
    return filename


async def compare_campaigns() -> str:
    campaigns = await db.get_campaigns()
    if not campaigns:
        return "No campaigns to compare."

    lines = "📊 **Campaign Comparison**\n\n"
    for c in campaigns:
        lines += (
            f"• {c['name']}: {c.get('invited', 0)} invited, "
            f"{c.get('joined', 0)} joined, {c.get('left', 0)} left\n"
        )
    return lines
