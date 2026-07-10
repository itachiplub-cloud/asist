import asyncio
import sys

from pyrogram import Client, idle
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler, ChatMemberUpdatedHandler
from pyrogram import filters as pyro_filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, OWNER_ID, DAILY_REPORT_TIME, WEEKLY_REPORT_DAY
from database import Database
from utils.logger import logger
from utils import client_manager

from modules import (
    start, help, invite, status, target, sudo, blacklist, stats,
    ai, analytics, notifications, session, cluster, plugin_market, scheduler,
    campaign, backup, security, export, translation, ticket, announcement,
    reward, recommendation, event, api_system, monitor,
)


async def main():
    if not all([API_ID, API_HASH, STRING_SESSION, BOT_TOKEN, OWNER_ID]):
        logger.error(
            "Missing required environment variables: "
            "API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, OWNER_ID"
        )
        sys.exit(1)

    db = Database()
    logger.info("Connected to MongoDB")

    # --- Userbot client (performs actions) ---
    userbot = Client(
        name="userbot",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=STRING_SESSION,
        parse_mode=ParseMode.MARKDOWN,
        sleep_threshold=30,
    )

    # --- Bot client (receives commands, replies) ---
    bot = Client(
        name="bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        parse_mode=ParseMode.MARKDOWN,
        sleep_threshold=30,
    )

    client_manager.userbot = userbot
    client_manager.bot = bot

    await userbot.start()
    logger.info(f"Userbot started as {userbot.me.first_name} (ID: {userbot.me.id})")

    await bot.start()
    logger.info(f"Bot started as {bot.me.first_name} (ID: {bot.me.id})")

    await bot.send_message(OWNER_ID, "🤖 **Assistant Bot is now online!**")

    # Register AI handlers on userbot (it receives chat events)
    from services.ai_service import handle_message, welcome_new_user
    userbot.add_handler(MessageHandler(handle_message, pyro_filters.text & ~pyro_filters.command(list(
        c.replace("/", "") for c in [
            "start", "help", "invite", "stopinvite", "invitestatus",
            "addsudo", "delsudo", "sudolist", "settarget", "target",
            "blacklist", "unblacklist", "ping", "stats",
            "enableai", "disableai", "rules", "moderate",
            "groupstats", "activity", "topmembers",
            "notify", "notifications",
            "sessionstatus", "restartsession",
            "addassistant", "removeassistant", "listassistants",
            "load", "unload", "reload", "plugins",
            "schedule", "listschedules", "cancelschedule",
            "createcampaign", "campaignstats", "deletecampaign",
            "backup", "restore", "autobackup",
            "security", "loginhistory",
            "export", "setlang", "translate",
            "ticket", "closeticket", "tickets",
            "announce", "pinannounce",
            "addreward", "redeemreward", "rewards",
            "recommend", "createevent", "events", "deleteevent",
            "apikey", "revokeapikey", "listapikeys", "system",
        ]
    ))))
    userbot.add_handler(ChatMemberUpdatedHandler(welcome_new_user))

    # Resume invite progress on userbot
    from modules.invite import resume_invite
    await resume_invite()

    # Start session health monitor for userbot
    from services.session_service import start_health_monitor
    await start_health_monitor()

    # Start resource monitor
    from services.monitor_service import start_task_monitor
    await start_task_monitor()

    # Start scheduler
    from services.scheduler_service import run_scheduler
    await run_scheduler()

    # Initialize cluster assistants
    from services.cluster_service import initialize_assistants
    await initialize_assistants()

    # Setup APScheduler for daily/weekly reports
    apscheduler = AsyncIOScheduler()
    from services.analytics_service import generate_daily_report, generate_weekly_report

    hour, minute = DAILY_REPORT_TIME.split(":")
    apscheduler.add_job(generate_daily_report, "cron", args=[], hour=int(hour), minute=int(minute))
    apscheduler.add_job(generate_weekly_report, "cron", args=[], day_of_week=0, hour=int(hour), minute=int(minute))

    apscheduler.start()

    logger.info("All services initialized")
    await idle()

    apscheduler.shutdown()
    await bot.stop()
    await userbot.stop()
    logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
