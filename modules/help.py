from pyrogram import Client, filters
from pyrogram.types import Message
from utils.permissions import is_authorized, is_owner
from utils.logger import logger


@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    if not await is_authorized(message.from_user.id):
        await message.reply("❌ You are not authorized to use this bot.")
        return

    logger.info(f"User {message.from_user.id} used /help")
    is_owner_user = await is_owner(message.from_user.id)

    owner_only = ""
    if is_owner_user:
        owner_only = (
            "👑 **Owner Commands:**\n"
            "• /addsudo <id> - Add sudo admin\n"
            "• /delsudo <id> - Remove sudo admin\n"
            "• /sudolist - List sudo admins\n"
            "• /settarget <id> - Set target group\n"
            "• /setlang <code> - Set group language\n"
            "• /notify <k> <on|off> - Notification settings\n"
            "• /notifications - View notification settings\n"
            "• /sessionstatus - Check session health\n"
            "• /restartsession - Restart session\n"
            "• /addassistant <ss> - Add cluster assistant\n"
            "• /removeassistant <id> - Remove assistant\n"
            "• /listassistants - List assistants\n"
            "• /load <plugin> - Load plugin\n"
            "• /unload <plugin> - Unload plugin\n"
            "• /reload <plugin> - Reload plugin\n"
            "• /plugins - List plugins\n"
            "• /schedule <type> <int> - Schedule task\n"
            "• /listschedules - List scheduled tasks\n"
            "• /cancelschedule <id> - Cancel task\n"
            "• /backup - Create backup\n"
            "• /restore [file] - Restore backup\n"
            "• /autobackup <on|off> - Toggle auto backup\n"
            "• /security - Security dashboard\n"
            "• /loginhistory [id] - Login history\n"
            "• /export <type> [fmt] - Export data\n"
            "• /announce <text> - Broadcast announcement\n"
            "• /pinannounce <text> - Pin announcement\n"
            "• /addreward <n> <p> <t> - Add reward\n"
            "• /createevent <n> <t> - Create event\n"
            "• /events - List events\n"
            "• /deleteevent <id> - Delete event\n"
            "• /apikey <name> [perm] - Create API key\n"
            "• /revokeapikey <key> - Revoke API key\n"
            "• /listapikeys - List API keys\n"
            "• /recommend - Smart recommendations\n"
            "• /system - System monitoring\n\n"
        )

    text = (
        "🤖 **Assistant Bot Help**\n\n"
        f"{owner_only}"
        "🛠 **Invite Commands:**\n"
        "• /invite <source> - Start inviting\n"
        "• /stopinvite - Stop invite process\n"
        "• /invitestatus - Current status\n"
        "• /createcampaign <n> <s> - Create campaign\n"
        "• /campaignstats <n> - Campaign stats\n"
        "• /deletecampaign <n> - Delete campaign\n"
        "• /blacklist <id> - Blacklist user\n"
        "• /unblacklist <id> - Unblacklist user\n\n"
        "🤖 **AI Commands:**\n"
        "• /enableai - Enable AI manager\n"
        "• /disableai - Disable AI manager\n"
        "• /rules - Show group rules\n"
        "• /moderate <a> <id> <r> - Suggest moderation\n\n"
        "📊 **Analytics:**\n"
        "• /groupstats - Group statistics\n"
        "• /activity - Activity chart\n"
        "• /topmembers - Top members\n\n"
        "🎟️ **Support:**\n"
        "• /ticket <issue> - Create ticket\n"
        "• /closeticket <id> - Close ticket\n"
        "• /tickets - List tickets\n\n"
        "🎁 **Rewards:**\n"
        "• /rewards - List rewards\n"
        "• /redeemreward <id> - Claim reward\n\n"
        "📢 **Utility:**\n"
        "• /target - View target group\n"
        "• /ping - Bot latency\n"
        "• /stats - Bot statistics\n"
        "• /translate - Translation info\n"
        "• /help - Show this menu\n\n"
        "⚠️ Only Owner and Sudo Admins can use this bot."
    )
    await message.reply(text)
