# ========================================
# Language Manager
# ========================================

from languages import ru, en

LANGUAGES = {
    "ru": ru,
    "en": en,
}

def get_text(lang: str, key: str):
    """Получение текста по ключу"""
    if lang not in LANGUAGES:
        lang = "ru"
    return getattr(LANGUAGES[lang], key, getattr(ru, key, ""))

def get_language_name(lang: str) -> str:
    """Название языка"""
    names = {"ru": "Русский", "en": "English"}
    return names.get(lang, "Русский")
