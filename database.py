from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME


class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[DB_NAME]

        self.sudo_users = self.db.sudo_users
        self.target_groups = self.db.target_groups
        self.invite_progress = self.db.invite_progress
        self.blacklist = self.db.blacklist
        self.campaigns = self.db.campaigns
        self.analytics_messages = self.db.analytics_messages
        self.analytics_daily = self.db.analytics_daily
        self.analytics_members = self.db.analytics_members
        self.notify_settings = self.db.notify_settings
        self.session_health = self.db.session_health
        self.assistants = self.db.assistants
        self.plugin_config = self.db.plugin_config
        self.plugins_meta = self.db.plugins_meta
        self.scheduled_tasks = self.db.scheduled_tasks
        self.security_audit = self.db.security_audit
        self.security_sessions = self.db.security_sessions
        self.tickets = self.db.tickets
        self.rewards = self.db.rewards
        self.reward_claims = self.db.reward_claims
        self.events = self.db.events
        self.api_keys = self.db.api_keys
        self.api_usage = self.db.api_usage
        self.translations = self.db.translations
        self.group_langs = self.db.group_langs
        self.announcements = self.db.announcements
        self.ai_config = self.db.ai_config
        self.ai_faq = self.db.ai_faq

    # ── Sudo Users ──
    async def add_sudo(self, user_id: int) -> bool:
        existing = await self.sudo_users.find_one({"user_id": user_id})
        if existing:
            return False
        await self.sudo_users.insert_one({"user_id": user_id})
        return True

    async def remove_sudo(self, user_id: int) -> bool:
        result = await self.sudo_users.delete_one({"user_id": user_id})
        return result.deleted_count > 0

    async def get_sudo_users(self) -> list:
        cursor = self.sudo_users.find({}, {"_id": 0, "user_id": 1})
        return [doc["user_id"] async for doc in cursor]

    async def is_sudo(self, user_id: int) -> bool:
        doc = await self.sudo_users.find_one({"user_id": user_id})
        return doc is not None

    # ── Target Groups ──
    async def set_target(self, chat_id: int, title: str = None) -> None:
        await self.target_groups.update_one(
            {"_id": "target"},
            {"$set": {"chat_id": chat_id, "title": title or str(chat_id)}},
            upsert=True,
        )

    async def get_target(self) -> dict | None:
        return await self.target_groups.find_one({"_id": "target"})

    # ── Invite Progress ──
    async def save_progress(self, data: dict) -> None:
        await self.invite_progress.update_one(
            {"_id": "current"},
            {"$set": data},
            upsert=True,
        )

    async def get_progress(self) -> dict | None:
        return await self.invite_progress.find_one({"_id": "current"})

    async def clear_progress(self) -> None:
        await self.invite_progress.delete_one({"_id": "current"})

    # ── Blacklist ──
    async def blacklist_user(self, user_id: int, reason: str = None) -> bool:
        existing = await self.blacklist.find_one({"user_id": user_id})
        if existing:
            return False
        await self.blacklist.insert_one({"user_id": user_id, "reason": reason or "Not specified"})
        return True

    async def unblacklist_user(self, user_id: int) -> bool:
        result = await self.blacklist.delete_one({"user_id": user_id})
        return result.deleted_count > 0

    async def is_blacklisted(self, user_id: int) -> bool:
        doc = await self.blacklist.find_one({"user_id": user_id})
        return doc is not None

    async def get_blacklist(self) -> list:
        cursor = self.blacklist.find({}, {"_id": 0, "user_id": 1, "reason": 1})
        return [doc async for doc in cursor]

    async def get_blacklist_count(self) -> int:
        return await self.blacklist.count_documents({})

    async def get_total_invited(self) -> int:
        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$invited_count"}}}]
        cursor = self.invite_progress.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        return result[0]["total"] if result else 0

    # ── Campaigns ──
    async def create_campaign(self, name: str, source_chat_id: int, target_chat_id: int) -> dict:
        doc = {
            "name": name,
            "source_chat_id": source_chat_id,
            "target_chat_id": target_chat_id,
            "invited": 0,
            "joined": 0,
            "left": 0,
            "created_at": None,
            "status": "active",
        }
        result = await self.campaigns.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def get_campaign(self, name: str) -> dict | None:
        return await self.campaigns.find_one({"name": name})

    async def get_campaigns(self) -> list:
        return [doc async for doc in self.campaigns.find({})]

    async def delete_campaign(self, name: str) -> bool:
        result = await self.campaigns.delete_one({"name": name})
        return result.deleted_count > 0

    async def update_campaign(self, name: str, update: dict) -> None:
        await self.campaigns.update_one({"name": name}, {"$set": update})

    # ── Analytics ──
    async def log_message(self, chat_id: int, user_id: int, media_type: str = None) -> None:
        await self.analytics_messages.insert_one({
            "chat_id": chat_id,
            "user_id": user_id,
            "media_type": media_type,
            "timestamp": None,
        })

    async def get_message_count(self, chat_id: int, since: float = 0) -> int:
        return await self.analytics_messages.count_documents({
            "chat_id": chat_id,
            "timestamp": {"$gte": since},
        })

    async def get_top_users(self, chat_id: int, since: float, limit: int = 10) -> list:
        pipeline = [
            {"$match": {"chat_id": chat_id, "timestamp": {"$gte": since}}},
            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]
        cursor = self.analytics_messages.aggregate(pipeline)
        return [doc async for doc in cursor]

    async def log_member_event(self, chat_id: int, event: str) -> None:
        await self.analytics_members.insert_one({
            "chat_id": chat_id,
            "event": event,
            "timestamp": None,
        })

    async def get_member_event_count(self, chat_id: int, event: str, since: float) -> int:
        return await self.analytics_members.count_documents({
            "chat_id": chat_id,
            "event": event,
            "timestamp": {"$gte": since},
        })

    async def get_hourly_activity(self, chat_id: int, since: float) -> list:
        pipeline = [
            {"$match": {"chat_id": chat_id, "timestamp": {"$gte": since}}},
            {"$group": {"_id": {"$hour": {"$toDate": {"$multiply": ["$timestamp", 1000]}}}, "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}},
        ]
        cursor = self.analytics_messages.aggregate(pipeline)
        return [doc async for doc in cursor]

    async def get_media_stats(self, chat_id: int, since: float) -> list:
        pipeline = [
            {"$match": {"chat_id": chat_id, "timestamp": {"$gte": since}, "media_type": {"$ne": None}}},
            {"$group": {"_id": "$media_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        cursor = self.analytics_messages.aggregate(pipeline)
        return [doc async for doc in cursor]

    async def save_daily_report(self, chat_id: int, date_str: str, data: dict) -> None:
        await self.analytics_daily.update_one(
            {"chat_id": chat_id, "date": date_str},
            {"$set": data},
            upsert=True,
        )

    # ── Notification Settings ──
    async def get_notify_settings(self, chat_id: int) -> dict:
        doc = await self.notify_settings.find_one({"chat_id": chat_id})
        if not doc:
            doc = {
                "chat_id": chat_id,
                "kick": True,
                "floodwait": True,
                "errors": True,
                "invite_done": True,
                "settings_change": True,
            }
            await self.notify_settings.insert_one(doc)
        return doc

    async def update_notify_setting(self, chat_id: int, key: str, value: bool) -> None:
        await self.notify_settings.update_one(
            {"chat_id": chat_id},
            {"$set": {key: value}},
            upsert=True,
        )

    # ── Session Health ──
    async def save_session_health(self, data: dict) -> None:
        await self.session_health.update_one(
            {"_id": "health"},
            {"$set": data},
            upsert=True,
        )

    async def get_session_health(self) -> dict | None:
        return await self.session_health.find_one({"_id": "health"})

    # ── Assistants ──
    async def add_assistant(self, session_string: str, name: str = None) -> dict:
        doc = {"session_string": session_string, "name": name or "Assistant", "active": True, "total_invited": 0, "errors": 0}
        result = await self.assistants.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def remove_assistant(self, assistant_id) -> bool:
        result = await self.assistants.delete_one({"_id": assistant_id})
        return result.deleted_count > 0

    async def get_assistants(self) -> list:
        return [doc async for doc in self.assistants.find({})]

    async def get_active_assistants(self) -> list:
        return [doc async for doc in self.assistants.find({"active": True})]

    async def update_assistant(self, assistant_id, update: dict) -> None:
        await self.assistants.update_one({"_id": assistant_id}, {"$set": update})

    # ── Plugin Config ──
    async def get_plugin_config(self, plugin_name: str) -> dict:
        doc = await self.plugin_config.find_one({"plugin": plugin_name})
        return doc or {"plugin": plugin_name, "enabled": True, "config": {}}

    async def set_plugin_config(self, plugin_name: str, config: dict) -> None:
        await self.plugin_config.update_one(
            {"plugin": plugin_name},
            {"$set": {"config": config}},
            upsert=True,
        )

    async def enable_plugin(self, plugin_name: str, enabled: bool) -> None:
        await self.plugin_config.update_one(
            {"plugin": plugin_name},
            {"$set": {"enabled": enabled}},
            upsert=True,
        )

    async def is_plugin_enabled(self, plugin_name: str) -> bool:
        doc = await self.plugin_config.find_one({"plugin": plugin_name})
        return doc.get("enabled", True) if doc else True

    async def register_plugin_meta(self, name: str, version: str, description: str, dependencies: list) -> None:
        await self.plugins_meta.update_one(
            {"name": name},
            {"$set": {"version": version, "description": description, "dependencies": dependencies}},
            upsert=True,
        )

    async def get_plugins_meta(self) -> list:
        return [doc async for doc in self.plugins_meta.find({})]

    # ── Scheduled Tasks ──
    async def create_scheduled_task(self, task: dict) -> dict:
        result = await self.scheduled_tasks.insert_one(task)
        task["_id"] = result.inserted_id
        return task

    async def get_scheduled_tasks(self) -> list:
        return [doc async for doc in self.scheduled_tasks.find({})]

    async def delete_scheduled_task(self, task_id) -> bool:
        result = await self.scheduled_tasks.delete_one({"_id": task_id})
        return result.deleted_count > 0

    # ── Security Audit ──
    async def log_audit(self, entry: dict) -> None:
        await self.security_audit.insert_one(entry)

    async def get_audit_logs(self, limit: int = 50) -> list:
        cursor = self.security_audit.find({}).sort("timestamp", -1).limit(limit)
        return [doc async for doc in cursor]

    async def log_login_attempt(self, user_id: int, success: bool, device: str = None) -> None:
        await self.security_sessions.insert_one({
            "user_id": user_id, "success": success,
            "device": device, "timestamp": None,
        })

    async def get_login_history(self, user_id: int, limit: int = 20) -> list:
        cursor = self.security_sessions.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
        return [doc async for doc in cursor]

    # ── Tickets ──
    async def create_ticket(self, user_id: int, issue: str, priority: str = "normal") -> dict:
        doc = {
            "user_id": user_id, "issue": issue, "priority": priority,
            "status": "open", "assigned_to": None, "logs": [],
            "created_at": None,
        }
        result = await self.tickets.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def close_ticket(self, ticket_id) -> bool:
        result = await self.tickets.update_one({"_id": ticket_id}, {"$set": {"status": "closed"}})
        return result.modified_count > 0

    async def assign_ticket(self, ticket_id, sudo_id: int) -> None:
        await self.tickets.update_one({"_id": ticket_id}, {"$set": {"assigned_to": sudo_id}})

    async def get_tickets(self, status: str = None) -> list:
        query = {"status": status} if status else {}
        return [doc async for doc in self.tickets.find(query)]

    # ── Rewards ──
    async def add_reward(self, name: str, points: int, reward_type: str) -> dict:
        doc = {"name": name, "points": points, "type": reward_type}
        result = await self.rewards.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def get_rewards(self) -> list:
        return [doc async for doc in self.rewards.find({})]

    async def claim_reward(self, user_id: int, reward_id) -> bool:
        existing = await self.reward_claims.find_one({"user_id": user_id, "reward_id": reward_id})
        if existing:
            return False
        await self.reward_claims.insert_one({"user_id": user_id, "reward_id": reward_id, "claimed_at": None})
        return True

    # ── Events ──
    async def create_event(self, name: str, event_type: str, config: dict) -> dict:
        doc = {"name": name, "type": event_type, "config": config, "status": "active"}
        result = await self.events.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def get_events(self) -> list:
        return [doc async for doc in self.events.find({})]

    async def delete_event(self, event_id) -> bool:
        result = await self.events.delete_one({"_id": event_id})
        return result.deleted_count > 0

    # ── API Keys ──
    async def create_api_key(self, name: str, permissions: list, rate_limit: int = 100) -> dict:
        import secrets
        key = f"invbot_{secrets.token_hex(16)}"
        doc = {"name": name, "key": key, "permissions": permissions, "rate_limit": rate_limit, "active": True}
        result = await self.api_keys.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def revoke_api_key(self, key: str) -> bool:
        result = await self.api_keys.update_one({"key": key}, {"$set": {"active": False}})
        return result.modified_count > 0

    async def get_api_keys(self) -> list:
        return [doc async for doc in self.api_keys.find({}, {"key": 1, "name": 1, "permissions": 1, "active": 1})]

    async def validate_api_key(self, key: str) -> dict | None:
        return await self.api_keys.find_one({"key": key, "active": True})

    async def log_api_usage(self, key: str, endpoint: str) -> None:
        await self.api_usage.insert_one({"key": key, "endpoint": endpoint, "timestamp": None})

    # ── Translations ──
    async def set_group_lang(self, chat_id: int, lang: str) -> None:
        await self.group_langs.update_one({"chat_id": chat_id}, {"$set": {"lang": lang}}, upsert=True)

    async def get_group_lang(self, chat_id: int) -> str:
        doc = await self.group_langs.find_one({"chat_id": chat_id})
        return doc.get("lang", "en") if doc else "en"

    async def set_translation(self, lang: str, key: str, text: str) -> None:
        await self.translations.update_one(
            {"lang": lang, "key": key},
            {"$set": {"text": text}},
            upsert=True,
        )

    async def get_translation(self, lang: str, key: str) -> str | None:
        doc = await self.translations.find_one({"lang": lang, "key": key})
        return doc.get("text") if doc else None

    # ── Announcements ──
    async def save_announcement(self, chat_id: int, text: str, media: str = None, buttons: list = None) -> dict:
        doc = {
            "chat_id": chat_id, "text": text, "media": media,
            "buttons": buttons or [], "created_at": None,
        }
        result = await self.announcements.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def get_group_chats(self) -> list:
        cursor = self.analytics_messages.distinct("chat_id")
        return await cursor

    # ── AI Config ──
    async def get_ai_config(self, chat_id: int) -> dict:
        doc = await self.ai_config.find_one({"chat_id": chat_id})
        if not doc:
            doc = {"chat_id": chat_id, "enabled": False}
            await self.ai_config.insert_one(doc)
        return doc

    async def set_ai_enabled(self, chat_id: int, enabled: bool) -> None:
        await self.ai_config.update_one({"chat_id": chat_id}, {"$set": {"enabled": enabled}}, upsert=True)

    async def add_faq(self, chat_id: int, pattern: str, answer: str) -> None:
        await self.ai_faq.update_one(
            {"chat_id": chat_id, "pattern": pattern},
            {"$set": {"answer": answer}},
            upsert=True,
        )

    async def get_faqs(self, chat_id: int) -> list:
        return [doc async for doc in self.ai_faq.find({"chat_id": chat_id})]
