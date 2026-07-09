from config import OWNER_ID
from database import Database

db = Database()


async def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


async def is_sudo(user_id: int) -> bool:
    return await db.is_sudo(user_id)


async def is_authorized(user_id: int) -> bool:
    return user_id == OWNER_ID or await db.is_sudo(user_id)
