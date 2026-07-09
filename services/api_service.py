from database import Database
from utils.logger import logger

db = Database()


async def create_api_key(name: str, permissions: list, rate_limit: int = 100) -> dict:
    result = await db.create_api_key(name, permissions, rate_limit)
    logger.info(f"API key created: {name}")
    return result


async def revoke_api_key(key: str) -> bool:
    success = await db.revoke_api_key(key)
    if success:
        logger.info(f"API key revoked: {key[:16]}...")
    return success


async def list_api_keys() -> str:
    keys = await db.get_api_keys()
    if not keys:
        return "No API keys found."

    lines = "🔑 **API Keys**\n\n"
    for k in keys:
        status = "✅" if k.get("active") else "❌"
        lines += f"{status} `{k['key'][:20]}...` | {k['name']} | {', '.join(k.get('permissions', []))}\n"
    return lines


async def validate_api_key(key: str) -> dict | None:
    return await db.validate_api_key(key)


async def log_api_usage(key: str, endpoint: str) -> None:
    await db.log_api_usage(key, endpoint)
