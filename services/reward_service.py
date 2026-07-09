import time

from database import Database
from utils.logger import logger

db = Database()


async def add_reward(name: str, points: int, reward_type: str) -> dict:
    reward = await db.add_reward(name, points, reward_type)
    logger.info(f"Reward added: {name} ({points}pts, {reward_type})")
    return reward


async def redeem_reward(user_id: int, reward_id) -> str:
    success = await db.claim_reward(user_id, reward_id)
    if success:
        logger.info(f"User {user_id} claimed reward {reward_id}")
        return "✅ Reward claimed successfully!"
    return "❌ You have already claimed this reward."


async def list_rewards() -> str:
    rewards = await db.get_rewards()
    if not rewards:
        return "No rewards available."

    lines = "🎁 **Available Rewards**\n\n"
    for r in rewards:
        lines += f"• {r['name']} ({r['points']} pts) - {r['type']}\n"
    return lines
