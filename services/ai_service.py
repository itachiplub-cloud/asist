import re
import time
from collections import defaultdict

from pyrogram import Client
from pyrogram.types import Message, ChatMemberUpdated
from config import OWNER_ID
from database import Database
from utils.logger import logger

db = Database()

SPAM_PATTERNS = [
    re.compile(r"(https?://[^\s]+)", re.I),
    re.compile(r"@\w{4,}", re.I),
    re.compile(r"(\+?\d[\d\s\-\(\)]{7,}\d)"),
    re.compile(r"(buy|sell|cheap|price|offer|discount|click|earn|free money|crypto)", re.I),
]

MESSAGE_FREQUENCY = defaultdict(list)
SPAM_THRESHOLD = 5
SPAM_WINDOW = 10


def is_spam(text: str) -> bool:
    if not text:
        return False
    score = 0
    for pattern in SPAM_PATTERNS:
        if pattern.search(text):
            score += 1
    return score >= 2


async def check_spam_frequency(user_id: int) -> bool:
    now = time.time()
    MESSAGE_FREQUENCY[user_id] = [t for t in MESSAGE_FREQUENCY[user_id] if now - t < SPAM_WINDOW]
    MESSAGE_FREQUENCY[user_id].append(now)
    return len(MESSAGE_FREQUENCY[user_id]) > SPAM_THRESHOLD


async def handle_message(client: Client, message: Message):
    chat_id = message.chat.id
    cfg = await db.get_ai_config(chat_id)
    if not cfg.get("enabled"):
        return

    if not message.text:
        return

    if await check_spam_frequency(message.from_user.id):
        try:
            await message.delete()
            await client.send_message(chat_id, f"⚠️ {message.from_user.mention} detected spamming.")
        except Exception as e:
            logger.warning(f"Spam delete failed: {e}")
        return

    if is_spam(message.text):
        try:
            await message.delete()
            await client.send_message(chat_id, f"⚠️ Spam message deleted.")
        except Exception as e:
            logger.warning(f"Spam delete failed: {e}")
        return

    faqs = await db.get_faqs(chat_id)
    for faq in faqs:
        if faq["pattern"].lower() in message.text.lower():
            await message.reply(faq["answer"])
            break


async def welcome_new_user(client: Client, chat_member_updated: ChatMemberUpdated):
    chat_id = chat_member_updated.chat.id
    cfg = await db.get_ai_config(chat_id)
    if not cfg.get("enabled"):
        return

    if chat_member_updated.new_chat_member and not chat_member_updated.old_chat_member:
        user = chat_member_updated.new_chat_member.user
        if not user.is_bot:
            welcome = (
                f"👋 Welcome {user.mention}!\n\n"
                "Please read the group rules and enjoy your stay."
            )
            await client.send_message(chat_id, welcome)


async def generate_rules(chat_id: int) -> str:
    return (
        "📜 **Group Rules**\n\n"
        "1. Be respectful to all members.\n"
        "2. No spam or self-promotion.\n"
        "3. No NSFW or offensive content.\n"
        "4. Stay on topic.\n"
        "5. Follow admin instructions.\n"
        "6. No harassment or bullying.\n"
        "7. Use English or the group's primary language.\n\n"
        "Violations may result in warnings, mutes, or bans."
    )


async def suggest_moderation(action: str, user_id: int, reason: str) -> str:
    return (
        f"🛡️ **Moderation Suggestion**\n"
        f"Action: {action}\n"
        f"User: `{user_id}`\n"
        f"Reason: {reason}"
    )
