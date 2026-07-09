import os

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
STRING_SESSION = os.getenv("STRING_SESSION", "")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "telegram_invite_bot")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

OWNER_ID = int(os.getenv("OWNER_ID", 0))

MAX_INVITES_PER_HOUR = int(os.getenv("MAX_INVITES_PER_HOUR", 25))
COOLDOWN_MIN = int(os.getenv("COOLDOWN_MIN", 45))
COOLDOWN_MAX = int(os.getenv("COOLDOWN_MAX", 60))
MAX_CONSECUTIVE_ERRORS = int(os.getenv("MAX_CONSECUTIVE_ERRORS", 3))
FLOODWAIT_LIMIT = int(os.getenv("FLOODWAIT_LIMIT", 3600))

BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
EXPORT_DIR = os.getenv("EXPORT_DIR", "exports")
API_PORT = int(os.getenv("API_PORT", 8000))
API_HOST = os.getenv("API_HOST", "0.0.0.0")

DEFAULT_LANG = os.getenv("DEFAULT_LANG", "en")
EMERGENCY_MODE = os.getenv("EMERGENCY_MODE", "false").lower() == "true"
DAILY_REPORT_TIME = os.getenv("DAILY_REPORT_TIME", "23:00")
WEEKLY_REPORT_DAY = os.getenv("WEEKLY_REPORT_DAY", "monday")
