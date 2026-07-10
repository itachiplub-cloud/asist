import asyncio
import sys

from pyrogram import Client, idle, filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler, ChatMemberUpdatedHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, OWNER_ID, DAILY_REPORT_TIME, WEEKLY_REPORT_DAY
from database import Database
from utils.logger import logger
from utils import client_manager

# ── Command handler imports ──
from modules.start import start_command
from modules.help import help_command
from modules.invite import invite_start, stop_invite, resume_invite
from modules.status import invite_status
from modules.target import set_target, target_info
from modules.sudo import add_sudo, del_sudo, sudo_list
from modules.blacklist import blacklist_user, unblacklist_user
from modules.stats import ping_command, stats_command
from modules.ai import enable_ai, disable_ai, rules_command, moderate_command
from modules.analytics import group_stats, activity_command, top_members
from modules.notifications import notify_settings, list_notifications
from modules.session import session_status, restart_session_cmd
from modules.cluster import add_assistant, remove_assistant, list_assistants
from modules.plugin_market import load_plugin_cmd, unload_plugin_cmd, reload_plugin_cmd, list_plugins
from modules.scheduler import schedule_task, list_schedules, cancel_schedule
from modules.campaign import create_campaign_cmd, campaign_stats, delete_campaign
from modules.backup import backup_cmd, restore_cmd, auto_backup
from modules.security import security_cmd, login_history
from modules.export import export_cmd
from modules.translation import set_lang, translate_cmd
from modules.ticket import ticket_cmd, close_ticket_cmd, tickets_cmd
from modules.announcement import announce_cmd, pin_announce
from modules.reward import add_reward_cmd, redeem_reward_cmd, rewards_cmd
from modules.recommendation import recommend_cmd
from modules.event import create_event_cmd, events_cmd, delete_event_cmd
from modules.api_system import api_key_cmd, revoke_api_key_cmd, list_api_keys_cmd
from modules.monitor import system_cmd

# ── Service imports ──
from services.ai_service import handle_message, welcome_new_user
from services.analytics_service import generate_daily_report, generate_weekly_report
from services.session_service import start_health_monitor, check_session_health
from services.monitor_service import start_task_monitor
from services.scheduler_service import run_scheduler
from services.cluster_service import initialize_assistants


HANDLERS = [
    # ── General ──
    (start_command, filters.command("start")),
    (help_command, filters.command("help")),
    (ping_command, filters.command("ping")),
    (stats_command, filters.command("stats")),

    # ── Sudo management (owner only) ──
    (add_sudo, filters.command("addsudo")),
    (del_sudo, filters.command("delsudo")),
    (sudo_list, filters.command("sudolist")),

    # ── Target group (owner only) ──
    (set_target, filters.command("settarget")),
    (target_info, filters.command("target")),

    # ── Invite ──
    (invite_start, filters.command("invite")),
    (stop_invite, filters.command("stopinvite")),
    (invite_status, filters.command("invitestatus")),

    # ── Blacklist ──
    (blacklist_user, filters.command("blacklist")),
    (unblacklist_user, filters.command("unblacklist")),

    # ── AI Group Manager ──
    (enable_ai, filters.command("enableai")),
    (disable_ai, filters.command("disableai")),
    (rules_command, filters.command("rules")),
    (moderate_command, filters.command("moderate")),

    # ── Analytics ──
    (group_stats, filters.command("groupstats")),
    (activity_command, filters.command("activity")),
    (top_members, filters.command("topmembers")),

    # ── Notifications (owner only) ──
    (notify_settings, filters.command("notify")),
    (list_notifications, filters.command("notifications")),

    # ── Session (owner only) ──
    (session_status, filters.command("sessionstatus")),
    (restart_session_cmd, filters.command("restartsession")),

    # ── Cluster (owner only) ──
    (add_assistant, filters.command("addassistant")),
    (remove_assistant, filters.command("removeassistant")),
    (list_assistants, filters.command("listassistants")),

    # ── Plugin marketplace (owner only) ──
    (load_plugin_cmd, filters.command("load")),
    (unload_plugin_cmd, filters.command("unload")),
    (reload_plugin_cmd, filters.command("reload")),
    (list_plugins, filters.command("plugins")),

    # ── Scheduler (owner only) ──
    (schedule_task, filters.command("schedule")),
    (list_schedules, filters.command("listschedules")),
    (cancel_schedule, filters.command("cancelschedule")),

    # ── Campaign ──
    (create_campaign_cmd, filters.command("createcampaign")),
    (campaign_stats, filters.command("campaignstats")),
    (delete_campaign, filters.command("deletecampaign")),

    # ── Backup (owner only) ──
    (backup_cmd, filters.command("backup")),
    (restore_cmd, filters.command("restore")),
    (auto_backup, filters.command("autobackup")),

    # ── Security (owner only) ──
    (security_cmd, filters.command("security")),
    (login_history, filters.command("loginhistory")),

    # ── Export (owner only) ──
    (export_cmd, filters.command("export")),

    # ── Translation ──
    (set_lang, filters.command("setlang")),
    (translate_cmd, filters.command("translate")),

    # ── Tickets ──
    (ticket_cmd, filters.command("ticket")),
    (close_ticket_cmd, filters.command("closeticket")),
    (tickets_cmd, filters.command("tickets")),

    # ── Announcements (owner only) ──
    (announce_cmd, filters.command("announce")),
    (pin_announce, filters.command("pinannounce")),

    # ── Rewards (owner only) ──
    (add_reward_cmd, filters.command("addreward")),
    (redeem_reward_cmd, filters.command("redeemreward")),
    (rewards_cmd, filters.command("rewards")),

    # ── Recommendations (owner only) ──
    (recommend_cmd, filters.command("recommend")),

    # ── Events (owner only) ──
    (create_event_cmd, filters.command("createevent")),
    (events_cmd, filters.command("events")),
    (delete_event_cmd, filters.command("deleteevent")),

    # ── API keys (owner only) ──
    (api_key_cmd, filters.command("apikey")),
    (revoke_api_key_cmd, filters.command("revokeapikey")),
    (list_api_keys_cmd, filters.command("listapikeys")),

    # ── System monitoring (owner only) ──
    (system_cmd, filters.command("system")),
]


async def main():
    if not all([API_ID, API_HASH, STRING_SESSION, BOT_TOKEN, OWNER_ID]):
        logger.error(
            "Missing required environment variables: "
            "API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, OWNER_ID"
        )
        sys.exit(1)

    db = Database()
    logger.info("Connected to MongoDB")

    # ── Userbot: performs actions (invite, moderate, announce, etc.) ──
    userbot = Client(
        name="userbot",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=STRING_SESSION,
        parse_mode=ParseMode.MARKDOWN,
        sleep_threshold=30,
    )

    # ── Bot: receives commands via DM, replies ──
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

    # Register command handlers on bot only
    for handler_fn, handler_filter in HANDLERS:
        bot.add_handler(MessageHandler(handler_fn, handler_filter))

    # Register AI handlers on userbot (spam detection, welcome, FAQ)
    userbot.add_handler(MessageHandler(handle_message, filters.text))
    userbot.add_handler(ChatMemberUpdatedHandler(welcome_new_user))

    await userbot.start()
    logger.info(f"Userbot started as {userbot.me.first_name} (ID: {userbot.me.id})")

    await bot.start()
    logger.info(f"Bot started as {bot.me.first_name} (ID: {bot.me.id})")

    await bot.send_message(OWNER_ID, "🤖 **Assistant Bot is now online!**")

    # ── Background services ──
    await resume_invite()
    await start_health_monitor()
    await start_task_monitor()
    await run_scheduler()
    await initialize_assistants()

    # ── Scheduled reports via APScheduler ──
    apscheduler = AsyncIOScheduler()
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
