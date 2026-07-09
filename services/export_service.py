import csv
import json
import os
from datetime import datetime
from io import StringIO

from config import EXPORT_DIR
from database import Database
from utils.logger import logger

db = Database()


async def export_users(fmt: str = "json") -> str | None:
    os.makedirs(EXPORT_DIR, exist_ok=True)
    filename = f"{EXPORT_DIR}/users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{fmt}"

    sudo_users = await db.get_sudo_users()
    blacklisted = await db.get_blacklist()
    data = {"sudo_users": sudo_users, "blacklisted_users": blacklisted}

    if fmt == "json":
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    elif fmt == "csv":
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["type", "user_id"])
            for uid in sudo_users:
                writer.writerow(["sudo", uid])
            for b in blacklisted:
                writer.writerow(["blacklisted", b["user_id"]])

    logger.info(f"Users exported to {filename}")
    return filename


async def export_groups(fmt: str = "json") -> str | None:
    os.makedirs(EXPORT_DIR, exist_ok=True)
    filename = f"{EXPORT_DIR}/groups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{fmt}"

    target = await db.get_target()
    data = {"target_group": target}

    if fmt == "json":
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    elif fmt == "csv":
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["chat_id", "title"])
            if target:
                writer.writerow([target.get("chat_id"), target.get("title")])

    logger.info(f"Groups exported to {filename}")
    return filename


async def export_logs(fmt: str = "json") -> str | None:
    os.makedirs(EXPORT_DIR, exist_ok=True)
    filename = f"{EXPORT_DIR}/logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{fmt}"

    logs = await db.get_audit_logs(100)
    data = [{"timestamp": l.get("timestamp"), "user_id": l.get("user_id"),
             "command": l.get("command"), "action": l.get("action")} for l in logs]

    if fmt == "json":
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    elif fmt == "csv":
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "user_id", "command", "action"])
            for d in data:
                writer.writerow([d.get("timestamp"), d.get("user_id"),
                                 d.get("command"), d.get("action")])

    logger.info(f"Logs exported to {filename}")
    return filename


async def export_stats(fmt: str = "json") -> str | None:
    os.makedirs(EXPORT_DIR, exist_ok=True)
    filename = f"{EXPORT_DIR}/stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{fmt}"

    target = await db.get_target()
    sudo_users = await db.get_sudo_users()
    blacklist_count = await db.get_blacklist_count()
    total_invited = await db.get_total_invited()

    data = {
        "target_set": bool(target),
        "sudo_count": len(sudo_users),
        "blacklist_count": blacklist_count,
        "total_invited": total_invited,
        "sudo_users": sudo_users,
    }

    if fmt == "json":
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    elif fmt == "csv":
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["metric", "value"])
            writer.writerow(["target_set", data["target_set"]])
            writer.writerow(["sudo_count", data["sudo_count"]])
            writer.writerow(["blacklist_count", data["blacklist_count"]])
            writer.writerow(["total_invited", data["total_invited"]])

    logger.info(f"Stats exported to {filename}")
    return filename
