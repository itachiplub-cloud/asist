import asyncio
import sys

from pyrogram import Client, idle
from pyrogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import API_ID, API_HASH, STRING_SESSION, OWNER_ID, DAILY_REPORT_TIME, WEEKLY_REPORT_DAY
from database import Database
from utils.logger import logger

from modules import (
    start, help, invite, status, target, sudo, blacklist, stats,
    ai, analytics, notifications, session, cluster, plugin_market, scheduler,
    campaign, backup, security, export, translation, ticket, announcement,
    reward, recommendation, event, api_system, monitor,
)


async def main():
    if not all([API_ID, API_HASH, STRING_SESSION, OWNER_ID]):
        logger.error(
            "Missing required environment variables: "
            "API_ID, API_HASH, STRING_SESSION, OWNER_ID"
        )
        sys.exit(1)

    db = Database()
    logger.info("Connected to MongoDB")

    app = Client(
        name="assistant_invite",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=STRING_SESSION,
        parse_mode=ParseMode.MARKDOWN,
        sleep_threshold=30,
    )

    await app.start()
    logger.info(f"Bot started as {app.me.first_name} (ID: {app.me.id})")

    await app.send_message(OWNER_ID, "🤖 **Assistant Invite Bot is now online!**")

    # Resume invite progress
    from modules.invite import resume_invite
    await resume_invite(app)

    # Start session health monitor
    from services.session_service import start_health_monitor
    await start_health_monitor(app)

    # Start resource monitor
    from services.monitor_service import start_task_monitor
    await start_task_monitor()

    # Start scheduler
    from services.scheduler_service import run_scheduler
    await run_scheduler(app)

    # Initialize cluster assistants
    from services.cluster_service import initialize_assistants
    await initialize_assistants()

    # Setup APScheduler for daily/weekly reports
    scheduler = AsyncIOScheduler()
    from services.analytics_service import generate_daily_report, generate_weekly_report

    hour, minute = DAILY_REPORT_TIME.split(":")
    scheduler.add_job(generate_daily_report, "cron", args=[app], hour=int(hour), minute=int(minute))

    weekday_map = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                   "friday": 4, "saturday": 5, "sunday": 6}
    wday = weekday_map.get(WEEKLY_REPORT_DAY.lower(), 0)
    scheduler.add_job(generate_weekly_report, "cron", args=[app], day_of_week=wday, hour=int(hour), minute=int(minute))

    scheduler.start()

    # Register Pyrogram handlers for AI
    from services.ai_service import handle_message, welcome_new_user
    from pyrogram import filters as pyro_filters
    from pyrogram.handlers import MessageHandler, ChatMemberUpdatedHandler

    app.add_handler(MessageHandler(handle_message, pyro_filters.text & ~pyro_filters.command(list(
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
    app.add_handler(ChatMemberUpdatedHandler(welcome_new_user))

    logger.info("All services initialized")
    await idle()

    scheduler.shutdown()
    await app.stop()
    logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
