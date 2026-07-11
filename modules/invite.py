import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid, UserIdInvalid
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message

from config import OWNER_ID, MAX_CONSECUTIVE_ERRORS, FLOODWAIT_LIMIT
from database import Database
from utils.permissions import is_authorized
from utils.helpers import safe_invite, get_cooldown, validate_chat_id
from utils.cooldown import CooldownManager
from utils.logger import logger
from utils import client_manager

db = Database()
invite_running: dict = {}


async def resume_invite():
    progress = await db.get_progress()
    if not progress:
        return

    source_id = progress["source_chat_id"]
    logger.info(f"Resuming invite process: {source_id} -> {progress['target_chat_id']}")
    invite_running[source_id] = True


async def invite_start(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    if len(message.command) < 2:
        await message.reply("Usage: /invite <source_chat_id>")
        return

    try:
        source_chat_id = int(message.command[1])
    except ValueError:
        await message.reply("❌ Invalid source chat ID.")
        return

    target = await db.get_target()
    if not target:
        await message.reply("❌ No target group set. Use /settarget first.")
        return

    target_chat_id = target["chat_id"]

    if source_chat_id == target_chat_id:
        await message.reply("❌ Source and target groups cannot be the same.")
        return

    if invite_running.get(source_chat_id, False):
        await message.reply("❌ An invite process is already running for this group.")
        return

    logger.info(f"Invite requested: {source_chat_id} -> {target_chat_id} by {message.from_user.id}")

    # Validate target group before starting
    ub = client_manager.userbot
    valid = await validate_chat_id(ub, target_chat_id)
    if not valid:
        logger.warning(f"Target group {target_chat_id} is invalid, clearing from DB")
        from database import Database
        dbl = Database()
        await dbl.target_groups.delete_one({"_id": "target"})
        await message.reply(f"❌ Target group `{target_chat_id}` is no longer accessible. Removed from database.")
        return

    msg = await message.reply("🔄 Starting invite process...")

    invite_running[source_chat_id] = True
    cooldown_mgr = CooldownManager()

    try:
        source_members = []
        async for member in ub.get_chat_members(source_chat_id):
            source_members.append(member)
    except Exception as e:
        invite_running[source_chat_id] = False
        await msg.edit(f"❌ Failed to fetch members: {e}")
        return

    if not source_members:
        invite_running[source_chat_id] = False
        await msg.edit("❌ No members found in the source group.")
        return

    await msg.edit(f"✅ Found {len(source_members)} members. Starting invites...")

    invited_count = 0
    skipped_count = 0
    error_count = 0
    consecutive_errors = 0
    privacy_restrictions = 0
    last_user_id = None

    for member in source_members:
        user = member.user
        user_id = user.id

        if not invite_running.get(source_chat_id, False):
            logger.info(f"Invite process stopped by user for {source_chat_id}")
            break

        should_skip = False
        skip_reason = ""

        if user.is_bot:
            should_skip, skip_reason = True, "bot"
        elif user.is_deleted:
            should_skip, skip_reason = True, "deleted"
        elif member.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR):
            should_skip, skip_reason = True, "admin"
        elif await db.is_blacklisted(user_id):
            should_skip, skip_reason = True, "blacklisted"

        if not should_skip:
            try:
                chat_member = await ub.get_chat_member(target_chat_id, user_id)
                if chat_member:
                    should_skip, skip_reason = True, "already_member"
            except (PeerIdInvalid, UserIdInvalid):
                pass
            except Exception:
                pass

        if should_skip:
            skipped_count += 1
            logger.debug(f"Skipped {user_id}: {skip_reason}")
            await db.save_progress({
                "source_chat_id": source_chat_id,
                "target_chat_id": target_chat_id,
                "last_user_id": user_id,
                "invited_count": invited_count,
                "skipped_count": skipped_count,
                "error_count": error_count,
            })
            continue

        if not cooldown_mgr.can_invite():
            logger.info(f"Hourly quota reached for {source_chat_id}")
            await client_manager.bot.send_message(
                OWNER_ID,
                f"⚠️ Hourly invite limit reached for source `{source_chat_id}`. Stopping."
            )
            break

        success, err = await safe_invite(ub, target_chat_id, user_id)

        if success:
            invited_count += 1
            consecutive_errors = 0
            cooldown_mgr.record_invite()
            last_user_id = user_id
            logger.info(f"Invited {user_id} to {target_chat_id}")
        else:
            consecutive_errors += 1
            error_count += 1
            skipped_count += 1

            if err == "flood_exceeded":
                logger.error(f"FloodWait > 1h, stopping invite for {source_chat_id}")
                await client_manager.bot.send_message(
                    OWNER_ID,
                    f"⚠️ FloodWait exceeded 1 hour. Invite process stopped for `{source_chat_id}`."
                )
                break
            elif err.startswith("invalid_peer:"):
                bad_chat_id = err.split(":", 1)[1]
                logger.error(f"Target group {bad_chat_id} is invalid, clearing from DB")
                await db.target_groups.delete_one({"_id": "target"})
                await client_manager.bot.send_message(
                    OWNER_ID,
                    f"⚠️ Target group `{bad_chat_id}` is invalid. Removed from database. Stopping invite."
                )
                break
            elif err == "privacy":
                privacy_restrictions += 1
                if privacy_restrictions >= 10:
                    logger.error(f"Too many privacy restrictions for {source_chat_id}")
                    await client_manager.bot.send_message(
                        OWNER_ID,
                        f"⚠️ Too many privacy restrictions. Stopping invite for `{source_chat_id}`."
                    )
                    break
            elif err == "already_member":
                pass
            elif err == "invalid_user":
                pass
            else:
                logger.warning(f"Error inviting {user_id}: {err}")

            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                logger.error(f"{MAX_CONSECUTIVE_ERRORS} consecutive errors, stopping for {source_chat_id}")
                await client_manager.bot.send_message(
                    OWNER_ID,
                    f"⚠️ {MAX_CONSECUTIVE_ERRORS} consecutive errors. Invite process stopped for `{source_chat_id}`."
                )
                break

        await db.save_progress({
            "source_chat_id": source_chat_id,
            "target_chat_id": target_chat_id,
            "last_user_id": last_user_id,
            "invited_count": invited_count,
            "skipped_count": skipped_count,
            "error_count": error_count,
        })

        cooldown = get_cooldown()
        logger.debug(f"Cooldown {cooldown}s for {source_chat_id}")
        for remaining in range(cooldown, 0, -1):
            if not invite_running.get(source_chat_id, False):
                logger.info("Cooldown interrupted by stop command")
                break
            if remaining % 10 == 0 or remaining <= 5:
                await msg.edit(
                    f"📊 **Invite Progress**\n\n"
                    f"Invited: {invited_count}\n"
                    f"Skipped: {skipped_count}\n"
                    f"Errors: {error_count}\n"
                    f"Cooldown: {remaining}s\n"
                    f"Running: Yes"
                )
            await asyncio.sleep(1)

    invite_running[source_chat_id] = False
    await db.clear_progress()

    summary = (
        "✅ **Invite Process Completed**\n\n"
        f"Invited: {invited_count}\n"
        f"Skipped: {skipped_count}\n"
        f"Errors: {error_count}"
    )
    await client_manager.bot.send_message(OWNER_ID, summary)
    await msg.edit(summary)
    logger.info(f"Invite process finished for {source_chat_id}")


async def stop_invite(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    progress = await db.get_progress()
    if not progress:
        await message.reply("❌ No invite process is currently running.")
        return

    source_id = progress["source_chat_id"]
    invite_running[source_id] = False
    logger.info(f"Invite process stopped by {message.from_user.id} for {source_id}")
    await message.reply("⏹️ Invite process stopped.")
