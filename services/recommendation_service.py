import time

from database import Database
from config import COOLDOWN_MIN, COOLDOWN_MAX
from utils.logger import logger

db = Database()


async def get_recommendations() -> str:
    recommendations = []

    last_24h = time.time() - 86400
    last_week = time.time() - 604800

    chats = set()
    async for doc in db.analytics_messages.find({"timestamp": {"$gte": last_week}}):
        chats.add(doc["chat_id"])

    for chat_id in chats:
        msg_count = await db.get_message_count(chat_id, last_24h)
        if msg_count < 10:
            recommendations.append(
                f"📉 Group `{chat_id}` is nearly inactive ({msg_count} msgs/24h). "
                "Consider a campaign or announcement."
            )

    hourly = {}
    for chat_id in chats:
        activity = await db.get_hourly_activity(chat_id, last_week)
        for h in activity:
            hour = h["_id"]
            hourly[hour] = hourly.get(hour, 0) + h["count"]

    if hourly:
        best_hour = max(hourly, key=hourly.get)
        recommendations.append(
            f"⏰ Best time for campaigns: ~{best_hour}:00 UTC "
            f"(peak activity: {hourly[best_hour]} msgs)."
        )

    cooldown_suggestion = (
        f"⚙️ Current cooldown: {COOLDOWN_MIN}-{COOLDOWN_MAX}s. "
        "Consider lowering if no FloodWait errors occur."
    )
    recommendations.append(cooldown_suggestion)

    assistants = await db.get_assistants()
    if len(assistants) > 1:
        recommendations.append(
            "👥 Multiple assistants available. "
            "Task distribution is active for load balancing."
        )

    return "🧠 **Smart Recommendations**\n\n" + "\n\n".join(
        f"{i+1}. {r}" for i, r in enumerate(recommendations)
    )
