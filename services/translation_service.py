from database import Database

db = Database()

TRANSLATIONS = {
    "en": {
        "not_authorized": "❌ You are not authorized to use this bot.",
        "bot_online": "🤖 **Assistant Invite Bot is now online!**",
        "welcome": "👋 Welcome {user}!",
        "spam_detected": "⚠️ Spam detected.",
        "rules": "📜 **Group Rules**\n1. Be respectful.\n2. No spam.\n3. No offensive content.",
    },
    "es": {
        "not_authorized": "❌ No estás autorizado para usar este bot.",
        "bot_online": "🤖 **¡El bot asistente está en línea!**",
        "welcome": "👋 ¡Bienvenido {user}!",
        "spam_detected": "⚠️ Spam detectado.",
        "rules": "📜 **Reglas del Grupo**\n1. Sé respetuoso.\n2. Sin spam.\n3. Sin contenido ofensivo.",
    },
    "pt": {
        "not_authorized": "❌ Você não está autorizado a usar este bot.",
        "bot_online": "🤖 **O bot assistente está online!**",
        "welcome": "👋 Bem-vindo {user}!",
        "spam_detected": "⚠️ Spam detectado.",
        "rules": "📜 **Regras do Grupo**\n1. Seja respeitoso.\n2. Sem spam.\n3. Sem conteúdo ofensivo.",
    },
    "ar": {
        "not_authorized": "❌ غير مصرح لك باستخدام هذا البوت.",
        "bot_online": "🤖 **بوت المساعد متصل الآن!**",
        "welcome": "👋 مرحبا {user}!",
        "spam_detected": "⚠️ تم اكتشاف رسائل مزعجة.",
        "rules": "📜 **قوانين المجموعة**\n1. كن محترماً.\n2. لا سبام.\n3. لا محتوى مسيء.",
    },
}


async def get_text(chat_id: int, key: str, **kwargs) -> str:
    lang = await db.get_group_lang(chat_id)
    translations = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    text = translations.get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text


async def set_language(chat_id: int, lang: str) -> bool:
    if lang not in TRANSLATIONS:
        return False
    await db.set_group_lang(chat_id, lang)
    return True


async def get_supported_languages() -> list:
    return list(TRANSLATIONS.keys())
