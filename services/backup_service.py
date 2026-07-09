import json
import os
import subprocess
import tarfile
from datetime import datetime

from config import BACKUP_DIR, MONGO_URI, DB_NAME
from database import Database
from utils.logger import logger

db = Database()


async def run_backup(client=None) -> str:
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{BACKUP_DIR}/backup_{timestamp}.tar.gz"

    # Dump MongoDB
    mongo_backup = f"{BACKUP_DIR}/mongo_{timestamp}"
    try:
        subprocess.run(
            ["mongodump", f"--uri={MONGO_URI}", f"--out={mongo_backup}"],
            capture_output=True, timeout=120,
        )
    except Exception as e:
        logger.warning(f"MongoDB dump failed: {e}")

    # Create tar archive
    with tarfile.open(filename, "w:gz") as tar:
        if os.path.isdir(mongo_backup):
            tar.add(mongo_backup, arcname=f"mongo_{timestamp}")
        if os.path.isdir("logs"):
            tar.add("logs", arcname="logs")

    # Cleanup temp
    if os.path.isdir(mongo_backup):
        import shutil
        shutil.rmtree(mongo_backup, ignore_errors=True)

    logger.info(f"Backup created: {filename}")
    return filename


async def restore_backup(backup_path: str) -> bool:
    if not os.path.isfile(backup_path):
        return False

    extract_dir = os.path.join(BACKUP_DIR, "restore_temp")
    os.makedirs(extract_dir, exist_ok=True)

    try:
        with tarfile.open(backup_path, "r:gz") as tar:
            tar.extractall(extract_dir)

        for item in os.listdir(extract_dir):
            mongo_path = os.path.join(extract_dir, item)
            if os.path.isdir(mongo_path):
                subprocess.run(
                    ["mongorestore", f"--uri={MONGO_URI}", mongo_path],
                    capture_output=True, timeout=300,
                )

        import shutil
        shutil.rmtree(extract_dir, ignore_errors=True)
        logger.info(f"Restored from {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        return False


async def toggle_autobackup(enabled: bool, interval_hours: int = 24) -> dict:
    from database import Database
    db = Database()
    setting = {
        "enabled": enabled,
        "interval_hours": interval_hours,
        "updated_at": datetime.now().isoformat(),
    }
    await db.db.autobackup_settings.update_one(
        {"_id": "config"},
        {"$set": setting},
        upsert=True,
    )
    return setting


async def get_backup_list() -> list:
    if not os.path.isdir(BACKUP_DIR):
        return []
    files = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.endswith(".tar.gz")],
        reverse=True,
    )
    return files[:20]
