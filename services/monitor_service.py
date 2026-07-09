import asyncio
import os
import time

from database import Database
from utils.logger import logger

db = Database()
_start_time = time.time()
_monitor_tasks: dict = {}


def get_uptime() -> str:
    seconds = int(time.time() - _start_time)
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)
    parts = []
    if days: parts.append(f"{days}d")
    if hours: parts.append(f"{hours}h")
    if minutes: parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)


def get_cpu_usage() -> float:
    try:
        with open("/proc/stat") as f:
            fields = f.readline().split()[1:5]
        values = [int(v) for v in fields]
        total = sum(values)
        idle = values[3]
        return round((1 - idle / total) * 100, 1)
    except Exception:
        return 0.0


def get_ram_usage() -> dict:
    try:
        with open("/proc/meminfo") as f:
            lines = f.readlines()
        mem_total = int([l for l in lines if "MemTotal" in l][0].split()[1])
        mem_avail = int([l for l in lines if "MemAvailable" in l][0].split()[1])
        used = mem_total - mem_avail
        return {
            "total_mb": round(mem_total / 1024, 1),
            "used_mb": round(used / 1024, 1),
            "percent": round((used / mem_total) * 100, 1),
        }
    except Exception:
        return {"total_mb": 0, "used_mb": 0, "percent": 0}


def get_disk_usage() -> dict:
    try:
        stat = os.statvfs(".")
        total = stat.f_frsize * stat.f_blocks
        free = stat.f_frsize * stat.f_bfree
        used = total - free
        return {
            "total_gb": round(total / (1024**3), 1),
            "used_gb": round(used / (1024**3), 1),
            "percent": round((used / total) * 100, 1),
        }
    except Exception:
        return {"total_gb": 0, "used_gb": 0, "percent": 0}


async def get_system_info() -> str:
    cpu = get_cpu_usage()
    ram = get_ram_usage()
    disk = get_disk_usage()
    uptime = get_uptime()

    return (
        "📡 **System Monitor**\n\n"
        f"🖥 CPU: {cpu}%\n"
        f"💾 RAM: {ram['used_mb']}/{ram['total_mb']} MB ({ram['percent']}%)\n"
        f"💽 Disk: {disk['used_gb']}/{disk['total_gb']} GB ({disk['percent']}%)\n"
        f"⏱ Uptime: {uptime}\n"
    )


async def start_task_monitor():
    async def _monitor():
        while True:
            await asyncio.sleep(300)
            cpu = get_cpu_usage()
            ram = get_ram_usage()
            if cpu > 90 or ram["percent"] > 90:
                logger.warning(f"High resource usage: CPU {cpu}%, RAM {ram['percent']}%")

    _monitor_tasks["resource"] = asyncio.create_task(_monitor())
