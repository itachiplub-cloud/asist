from config import OWNER_ID
from database import Database
from utils.logger import logger

db = Database()


async def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


async def is_sudo(user_id: int) -> bool:
    try:
        return await db.is_sudo(user_id)
    except Exception as e:
        logger.error(f"Database error in is_sudo: {e}")
        return False


async def is_authorized(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    try:
        return await db.is_sudo(user_id)
    except Exception as e:
        logger.error(f"Database error in is_authorized: {e}")
        return False
