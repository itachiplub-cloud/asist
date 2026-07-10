import time
from datetime import datetime, timedelta

from config import OWNER_ID
from database import Database
from utils import client_manager
from utils.logger import logger

db = Database()


async def track_message(chat_id: int, user_id: int, media_type: str = None) -> None:
    await db.log_message(chat_id, user_id, media_type)


async def track_member_join(chat_id: int) -> None:
    await db.log_member_event(chat_id, "join")


async def track_member_leave(chat_id: int) -> None:
    await db.log_member_event(chat_id, "leave")


async def generate_daily_report() -> None:
    bot = client_manager.bot
    today = datetime.now().strftime("%Y-%m-%d")
    since = time.time() - 86400
    chats = set()
    async for doc in db.analytics_messages.find({"timestamp": {"$gte": since}}):
        chats.add(doc["chat_id"])

    for chat_id in chats:
        msg_count = await db.get_message_count(chat_id, since)
        joins = await db.get_member_event_count(chat_id, "join", since)
        leaves = await db.get_member_event_count(chat_id, "leave", since)
        top = await db.get_top_users(chat_id, since, 5)
        media = await db.get_media_stats(chat_id, since)
        hourly = await db.get_hourly_activity(chat_id, since)

        top_text = "\n".join([f"• `{u['_id']}` - {u['count']} msgs" for u in top]) or "N/A"
        media_text = "\n".join([f"• {m['_id'] or 'text'}: {m['count']}" for m in media]) or "N/A"
        peak = max(hourly, key=lambda x: x["count"])["_id"] if hourly else "N/A"

        report = (
            f"📊 **Daily Report ({today})**\n\n"
            f"Messages: {msg_count}\n"
            f"Joins: {joins} | Leaves: {leaves}\n"
            f"Peak Hour: {peak}:00\n"
            f"Growth: +{joins - leaves}\n\n"
            f"**Top Members:**\n{top_text}\n\n"
            f"**Media Stats:**\n{media_text}"
        )

        await db.save_daily_report(chat_id, today, {
            "messages": msg_count, "joins": joins, "leaves": leaves,
            "top_users": top, "media_stats": media, "peak_hour": peak,
        })

        try:
            await bot.send_message(OWNER_ID, f"📋 Daily Report for `{chat_id}`:\n\n{report}")
        except Exception as e:
            logger.warning(f"Failed to send daily report for {chat_id}: {e}")


async def generate_weekly_report() -> None:
    bot = client_manager.bot
    since = time.time() - 7 * 86400
    week_end = datetime.now().strftime("%Y-%m-%d")
    week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    chats = set()
    async for doc in db.analytics_messages.find({"timestamp": {"$gte": since}}):
        chats.add(doc["chat_id"])

    for chat_id in chats:
        msg_count = await db.get_message_count(chat_id, since)
        joins = await db.get_member_event_count(chat_id, "join", since)
        leaves = await db.get_member_event_count(chat_id, "leave", since)
        top = await db.get_top_users(chat_id, since, 10)

        top_text = "\n".join([f"• `{u['_id']}` - {u['count']} msgs" for u in top]) or "N/A"

        report = (
            f"📊 **Weekly Report ({week_start} to {week_end})**\n\n"
            f"Total Messages: {msg_count}\n"
            f"Joins: {joins} | Leaves: {leaves}\n"
            f"Net Growth: +{joins - leaves}\n\n"
            f"**Top 10 Members:**\n{top_text}"
        )

        try:
            await bot.send_message(OWNER_ID, f"📋 Weekly Report for `{chat_id}`:\n\n{report}")
        except Exception as e:
            logger.warning(f"Failed to send weekly report for {chat_id}: {e}")
