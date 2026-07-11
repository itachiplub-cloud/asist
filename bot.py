import asyncio
import os
import sys
import time

from pyrogram import Client, idle, filters
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from pyrogram.handlers import MessageHandler, ChatMemberUpdatedHandler
from pyrogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import (
    API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, OWNER_ID,
    DAILY_REPORT_TIME, WEEKLY_REPORT_DAY, MONGO_URI, DB_NAME,
)
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


_start_time = time.time()


def _make_safe(handler_fn):
    """Wrap a handler with try/except so user sees errors instead of silent failure."""
    async def safe(client, message):
        try:
            await handler_fn(client, message)
        except Exception as e:
            logger.exception(f"Handler {handler_fn.__name__} crashed: {e}")
            try:
                await message.reply(
                    f"❌ Internal error in `{handler_fn.__name__}`:\n`{e}`\n\n"
                    f"Check logs for details."
                )
            except Exception:
                pass
    return safe


_MODULE_HANDLERS = [
    # ── General ──
    (start_command, filters.command("start") & filters.private),
    (help_command, filters.command("help") & filters.private),
    (stats_command, filters.command("stats") & filters.private),

    # ── Sudo management (owner only) ──
    (add_sudo, filters.command("addsudo") & filters.private),
    (del_sudo, filters.command("delsudo") & filters.private),
    (sudo_list, filters.command("sudolist") & filters.private),

    # ── Target group (owner only) ──
    (set_target, filters.command("settarget") & filters.private),
    (target_info, filters.command("target") & filters.private),

    # ── Invite ──
    (invite_start, filters.command("invite") & filters.private),
    (stop_invite, filters.command("stopinvite") & filters.private),
    (invite_status, filters.command("invitestatus") & filters.private),

    # ── Blacklist ──
    (blacklist_user, filters.command("blacklist") & filters.private),
    (unblacklist_user, filters.command("unblacklist") & filters.private),

    # ── AI Group Manager ──
    (enable_ai, filters.command("enableai") & filters.private),
    (disable_ai, filters.command("disableai") & filters.private),
    (rules_command, filters.command("rules")),
    (moderate_command, filters.command("moderate") & filters.private),

    # ── Analytics ──
    (group_stats, filters.command("groupstats") & filters.private),
    (activity_command, filters.command("activity") & filters.private),
    (top_members, filters.command("topmembers") & filters.private),

    # ── Notifications (owner only) ──
    (notify_settings, filters.command("notify") & filters.private),
    (list_notifications, filters.command("notifications") & filters.private),

    # ── Session (owner only) ──
    (session_status, filters.command("sessionstatus") & filters.private),
    (restart_session_cmd, filters.command("restartsession") & filters.private),

    # ── Cluster (owner only) ──
    (add_assistant, filters.command("addassistant") & filters.private),
    (remove_assistant, filters.command("removeassistant") & filters.private),
    (list_assistants, filters.command("listassistants") & filters.private),

    # ── Plugin marketplace (owner only) ──
    (load_plugin_cmd, filters.command("load") & filters.private),
    (unload_plugin_cmd, filters.command("unload") & filters.private),
    (reload_plugin_cmd, filters.command("reload") & filters.private),
    (list_plugins, filters.command("plugins") & filters.private),

    # ── Scheduler (owner only) ──
    (schedule_task, filters.command("schedule") & filters.private),
    (list_schedules, filters.command("listschedules") & filters.private),
    (cancel_schedule, filters.command("cancelschedule") & filters.private),

    # ── Campaign ──
    (create_campaign_cmd, filters.command("createcampaign") & filters.private),
    (campaign_stats, filters.command("campaignstats") & filters.private),
    (delete_campaign, filters.command("deletecampaign") & filters.private),

    # ── Backup (owner only) ──
    (backup_cmd, filters.command("backup") & filters.private),
    (restore_cmd, filters.command("restore") & filters.private),
    (auto_backup, filters.command("autobackup") & filters.private),

    # ── Security (owner only) ──
    (security_cmd, filters.command("security") & filters.private),
    (login_history, filters.command("loginhistory") & filters.private),

    # ── Export (owner only) ──
    (export_cmd, filters.command("export") & filters.private),

    # ── Translation ──
    (set_lang, filters.command("setlang") & filters.private),
    (translate_cmd, filters.command("translate") & filters.private),

    # ── Tickets ──
    (ticket_cmd, filters.command("ticket") & filters.private),
    (close_ticket_cmd, filters.command("closeticket") & filters.private),
    (tickets_cmd, filters.command("tickets") & filters.private),

    # ── Announcements (owner only) ──
    (announce_cmd, filters.command("announce") & filters.private),
    (pin_announce, filters.command("pinannounce") & filters.private),

    # ── Rewards (owner only) ──
    (add_reward_cmd, filters.command("addreward") & filters.private),
    (redeem_reward_cmd, filters.command("redeemreward") & filters.private),
    (rewards_cmd, filters.command("rewards") & filters.private),

    # ── Recommendations (owner only) ──
    (recommend_cmd, filters.command("recommend") & filters.private),

    # ── Events (owner only) ──
    (create_event_cmd, filters.command("createevent") & filters.private),
    (events_cmd, filters.command("events") & filters.private),
    (delete_event_cmd, filters.command("deleteevent") & filters.private),

    # ── API keys (owner only) ──
    (api_key_cmd, filters.command("apikey") & filters.private),
    (revoke_api_key_cmd, filters.command("revokeapikey") & filters.private),
    (list_api_keys_cmd, filters.command("listapikeys") & filters.private),

    # ── System monitoring (owner only) ──
    (system_cmd, filters.command("system") & filters.private),
]


FLAG_FILE = "/tmp/bot_started.flag"
MIN_RESTART_INTERVAL = 60  # seconds — prevent crashloop


async def _safe_start(client, label):
    """Start a client with FloodWait handling. Retries if rate-limited."""
    attempt = 0
    while True:
        try:
            if client.is_connected:
                logger.info(f"{label} already connected, skipping start")
                return
            logger.info(f"Starting {label}...")
            await client.start()
            logger.info(f"{label} started as {client.me.first_name} (ID: {client.me.id})")
            return
        except FloodWait as e:
            wait = e.value + 5
            logger.warning(f"FloodWait on {label}: sleeping {wait}s (value={e.value})")
            await asyncio.sleep(wait)
            attempt += 1
            if attempt >= 5:
                logger.error(f"Giving up on {label} after {attempt} FloodWait retries")
                raise


async def main():
    # ── Startup gate: exit early if process restarted too fast ──
    if os.path.exists(FLAG_FILE):
        try:
            mtime = os.path.getmtime(FLAG_FILE)
            elapsed = time.time() - mtime
            if elapsed < MIN_RESTART_INTERVAL:
                remaining = int(MIN_RESTART_INTERVAL - elapsed)
                logger.error(
                    f"Process restarted too fast ({elapsed:.0f}s < {MIN_RESTART_INTERVAL}s). "
                    f"Sleeping {remaining}s before continuing to avoid auth FloodWait."
                )
                await asyncio.sleep(remaining)
        except OSError:
            pass

    with open(FLAG_FILE, "w") as f:
        f.write(str(time.time()))

    if not all([API_ID, API_HASH, STRING_SESSION, BOT_TOKEN, OWNER_ID]):
        logger.error(
            "Missing required environment variables: "
            "API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, OWNER_ID"
        )
        sys.exit(1)

    db = Database()
    logger.info("Database client created")

    # ── Userbot: performs actions (invite, moderate, announce, etc.) ──
    userbot = Client(
        name="userbot",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=STRING_SESSION,
        parse_mode=ParseMode.MARKDOWN,
        sleep_threshold=30,
        in_memory=True,
    )

    # ── Bot: receives commands via DM, replies ──
    bot = Client(
        name="bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        parse_mode=ParseMode.MARKDOWN,
        sleep_threshold=30,
        in_memory=True,
    )

    client_manager.userbot = userbot
    client_manager.bot = bot

    # ── Start clients with FloodWait safety ──
    await _safe_start(userbot, "Userbot")
    await _safe_start(bot, "Bot")

    # Delete any existing webhook (prevents polling conflict)
    try:
        await bot.delete_webhook()
        logger.info("Webhook cleared")
    except Exception as e:
        logger.warning(f"Failed to delete webhook (non-fatal): {e}")

    # Set bot command menu
    try:
        await bot.set_bot_commands([
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help menu"),
            BotCommand("ping", "Check latency"),
            BotCommand("stats", "Bot statistics"),
        ])
        logger.info("Bot commands set")
    except Exception as e:
        logger.warning(f"Failed to set bot commands (non-fatal): {e}")

    # ── Debug handler: log every incoming message (lowest priority) ──
    async def _echo(client, message):
        logger.info(f"Bot received: '{message.text}' from {message.from_user.id} in chat {message.chat.id}")
    bot.add_handler(MessageHandler(_echo, filters.all), group=1)

    # ── Minimal working commands (no module dependency) ──
    @bot.on_message(filters.command("ping") & filters.private)
    async def _ping(_, message):
        before = time.time()
        m = await message.reply("🏓 Pong!")
        after = time.time()
        await m.edit_text(f"🏓 **Pong!** `{round((after - before) * 1000, 2)}ms`")

    @bot.on_message(filters.command("debug") & filters.private)
    async def _debug(_, message):
        lines = [
            "🔍 **Bot Debug Report**",
            "",
            f"🕐 Uptime: {int(time.time() - _start_time)}s",
            f"🤖 Bot: @{bot.me.username or 'N/A'} (ID: {bot.me.id})",
            f"👤 Userbot: @{userbot.me.username or 'N/A'} (ID: {userbot.me.id})",
            f"👑 Owner ID: `{OWNER_ID}`",
            f"📦 Module handlers: {registered}",
            f"🛢️ MongoDB URI: `{MONGO_URI}`",
            f"🛢️ DB Name: `{DB_NAME}`",
            f"🔄 Webhook: cleared",
            "",
            "**Your info:**",
            f"🆔 Your ID: `{message.from_user.id}`",
            f"👤 Name: {message.from_user.first_name}",
            f"✅ Match Owner: {'YES' if message.from_user.id == OWNER_ID else 'NO'}",
        ]
        await message.reply("\n".join(lines))

    # ── Register module command handlers with error wrapping ──
    registered = 0
    for handler_fn, handler_filter in _MODULE_HANDLERS:
        bot.add_handler(MessageHandler(_make_safe(handler_fn), handler_filter))
        registered += 1
    logger.info(f"Registered {registered} module command handlers on bot")

    # Register AI handlers on userbot (spam detection, welcome, FAQ)
    userbot.add_handler(MessageHandler(handle_message, filters.text))
    userbot.add_handler(ChatMemberUpdatedHandler(welcome_new_user))

    await bot.send_message(
        OWNER_ID,
        "🤖 **Assistant Bot is now online!**\n\n"
        f"Handlers: {registered}\n"
        f"Userbot: @{userbot.me.username or userbot.me.first_name}\n"
        f"Bot: @{bot.me.username or bot.me.first_name}\n"
        f"Assistant sessions: lazy (start on first use)\n"
        f"Send /debug to see full status."
    )

    # ── Background services (each individually wrapped so a failure doesn't kill the process) ──
    for service_name, service_coro in [
        ("resume_invite", resume_invite()),
        ("start_health_monitor", start_health_monitor()),
        ("start_task_monitor", start_task_monitor()),
        ("run_scheduler", run_scheduler()),
        ("initialize_assistants", initialize_assistants()),
    ]:
        try:
            await service_coro
            logger.info(f"Background service '{service_name}' started")
        except Exception as e:
            logger.error(f"Background service '{service_name}' failed (non-fatal): {e}")

    # ── Scheduled reports via APScheduler ──
    try:
        apscheduler = AsyncIOScheduler()
        hour, minute = DAILY_REPORT_TIME.split(":")
        apscheduler.add_job(generate_daily_report, "cron", args=[], hour=int(hour), minute=int(minute))
        apscheduler.add_job(generate_weekly_report, "cron", args=[], day_of_week=0, hour=int(hour), minute=int(minute))
        apscheduler.start()
        logger.info("APScheduler started")
    except Exception as e:
        logger.warning(f"Failed to start APScheduler (non-fatal): {e}")

    logger.info("All services initialized")
    await idle()

    try:
        apscheduler.shutdown()
    except Exception:
        pass
    await bot.stop()
    await userbot.stop()
    logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
