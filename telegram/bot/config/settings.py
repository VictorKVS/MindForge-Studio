# ========================================
# Конфигурация бота
# Версия: 1.0.0
# ========================================

import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv(dotenv_path=Path(__file__).parent.parent / "config.env")

# Безопасность
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

if not BOT_TOKEN:
    raise ValueError(" BOT_TOKEN не найден в config.env!")

# Пути
BASE_DIR = Path(__file__).parent.parent
LOG_DIR = BASE_DIR / "logs"
ORDERS_DIR = BASE_DIR / "orders" / "incoming"
UPLOADS_DIR = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "bot_database.db"

# Создание папок
LOG_DIR.mkdir(exist_ok=True)
ORDERS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# Лимиты
MAX_MESSAGES = 10000
MAX_FILE_SIZE_MB = 10
AUTO_DELETE_DAYS = 90

# Настройки заказа
ORDER_PREFIX = "ART"
