# ========================================
# MindForge Telegram Bot v3.0
# С встроенной базой данных (10,000 сообщений)
# ========================================

import os
import yaml
import logging
import json
from pathlib import Path
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)
from dotenv import load_dotenv
from database import get_database

# ========================================
# Константы и пути
# ========================================
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "logs"
ORDERS_DIR = BASE_DIR / "orders" / "incoming"
LOG_DIR.mkdir(exist_ok=True)
ORDERS_DIR.mkdir(parents=True, exist_ok=True)

# ========================================
# Логирование
# ========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("tg-order-bot")

# ========================================
# Загрузка конфигурации
# ========================================
load_dotenv(dotenv_path=BASE_DIR / "config.env")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# ========================================
# База данных
# ========================================
db = get_database()

# ========================================
# Состояния FSM
# ========================================
ORDER_TYPE, ORDER_STYLE, ORDER_DEADLINE, ORDER_EXTRA, ORDER_CONFIRM = range(5)

# ========================================
# Тексты
# ========================================
WELCOME_TEXT = """
 MINDFORGE STUDIO
Индивидуальные визуальные работы по частному заказу.

 Персональный подход
 Контроль качества
 Конфиденциальность

Выберите действие ниже.
"""

# ========================================
# Вспомогательные функции
# ========================================
def log_event(event_type: str, user=None, payload=None):
    data = {"event": event_type, "timestamp": datetime.utcnow().isoformat()}
    if user:
        data["user"] = {"id": user.id, "username": user.username}
    if payload:
        data.update(payload)
    
    logger.info(f"[{event_type}] {data}")
    
    # Логирование в базу данных
    if user:
        db.log_event(event_type, user.id, payload or {})

def log_message(user, message_text: str, message_type: str):
    """Логирование сообщения в базу"""
    db.log_message(
        user_id=user.id,
        message_text=message_text,
        message_type=message_type,
        chat_id=user.id
    )

def build_keyboard(buttons):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=data) for text, data in row]
        for row in buttons
    ])

# ========================================
# Клавиатуры
# ========================================
def main_menu_keyboard():
    return build_keyboard([
        [(" Новый заказ", "menu:new_order")],
        [(" Пакеты и условия", "menu:packages")],
        [(" Статус заказа", "menu:status")],
        [(" Связь со студией", "menu:contact")],
        [(" Моя статистика", "menu:stats")],
    ])

def order_type_keyboard():
    return build_keyboard([
        [(" Одно изображение", "order:type:single")],
        [(" Серия работ", "order:type:series")],
        [(" Консультация", "order:type:consult")],
        [(" Назад", "menu:main")],
    ])

def order_confirm_keyboard():
    return build_keyboard([
        [(" Подтвердить", "order:confirm")],
        [(" Изменить", "order:edit")],
        [(" Отменить", "order:cancel")],
    ])

# ========================================
# Обработчики
# ========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Сохранение пользователя в базу
    db.upsert_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Логирование сообщения
    log_message(user, "/start", "command")
    
    log_event("start", user=user)
    await update.message.reply_text(WELCOME_TEXT, reply_markup=main_menu_keyboard())

async def on_menu_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data
    
    # Логирование нажатия
    log_message(user, f"Button: {data}", "callback")
    
    if data == "menu:main":
        await query.message.edit_text(WELCOME_TEXT, reply_markup=main_menu_keyboard())
        return
    
    action = data.split(":", 1)[1]
    log_event("menu_click", user=user, payload={"action": action})
    
    if action == "new_order":
        return await start_order_fsm(update, context)
    elif action == "packages":
        await query.message.reply_text(
            " **Пакеты и условия**\n\n"
            " Стандарт  базовая работа\n"
            " Премиум  приоритет и доработка\n"
            " Эксклюзив  полный контроль\n\n"
            "Детали обсуждаются после приёма заказа.",
            parse_mode="Markdown"
        )
    elif action == "status":
        await query.message.reply_text("Введите номер заказа (например, ART-20260219-001):")
    elif action == "contact":
        await query.message.reply_text("Администратор: @your_admin_username")
    elif action == "stats":
        # Статистика пользователя
        user_orders = db.get_user_orders(user.id)
        await query.message.reply_text(
            f" **Ваша статистика**\n\n"
            f" Заказов: {len(user_orders)}\n"
            f" Подтверждено: {len([o for o in user_orders if o['status'] == 'confirmed'])}\n\n"
            f"Последний заказ: {user_orders[0]['order_id'] if user_orders else 'Нет'}",
            parse_mode="Markdown"
        )

async def handle_status_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка статуса заказа"""
    user = update.effective_user
    message_text = update.message.text.strip()
    
    # Логирование сообщения
    log_message(user, message_text, "text")
    
    # Проверка формата номера заказа
    if not message_text.startswith("ART-"):
        await update.message.reply_text(" Неверный формат номера заказа.\nПример: ART-20260219-001")
        return
    
    order = db.get_order(message_text)
    
    if order:
        await update.message.reply_text(
            f" **Статус заказа**\n\n"
            f" ID: `{order['order_id']}`\n"
            f" Тип: {order['order_type']}\n"
            f" Стиль: {order['style']}\n"
            f" Сроки: {order['deadline']}\n"
            f" Статус: **{order['status']}**",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(f" Заказ {message_text} не найден")

# ========================================
# FSM Handlers
# ========================================
async def start_order_fsm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    context.user_data["order"] = {}
    log_event("order_fsm_start", user=user)
    await query.message.reply_text(" Выберите тип заказа:", reply_markup=order_type_keyboard())
    return ORDER_TYPE

async def order_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data
    order_type = data.split(":", 2)[2]
    type_map = {"single": "Одно изображение", "series": "Серия работ", "consult": "Консультация"}
    context.user_data["order"]["type"] = type_map[order_type]
    
    # Логирование выбора
    log_message(user, f"Выбор типа: {type_map[order_type]}", "order_step")
    
    log_event("order_type_selected", user=user, payload={"type": type_map[order_type]})
    await query.message.reply_text(" Укажите желаемый стиль (например, киберпанк, фэнтези):")
    return ORDER_STYLE

async def handle_order_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    style = update.message.text.strip()
    context.user_data["order"]["style"] = style
    
    # Логирование сообщения
    log_message(user, f"Стиль: {style}", "order_step")
    
    log_event("order_style_received", user=user, payload={"style": style})
    await update.message.reply_text(" Укажите сроки выполнения (например, нужно за 3 дня):")
    return ORDER_DEADLINE

async def handle_order_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    deadline = update.message.text.strip()
    context.user_data["order"]["deadline"] = {"raw": deadline}
    
    # Логирование сообщения
    log_message(user, f"Сроки: {deadline}", "order_step")
    
    log_event("order_deadline_received", user=user, payload={"deadline": deadline})
    await update.message.reply_text(" Дополнительные пожелания (если нет  напишите нет):")
    return ORDER_EXTRA

async def handle_order_extra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text.strip()
    extra = None if text.lower() in ("нет", "no", "none", "-") else text
    context.user_data["order"]["extra"] = extra
    
    # Логирование сообщения
    log_message(user, f"Дополнительно: {extra or 'Нет'}", "order_step")
    
    log_event("order_extra_received", user=user, payload={"extra": extra})
    order = context.user_data["order"]
    summary = (
        " *Подтверждение заказа*\n\n"
        f" *Тип:* {order.get('type')}\n"
        f" *Стиль:* {order.get('style')}\n"
        f" *Сроки:* {order.get('deadline', {}).get('raw')}\n"
        f" *Дополнительно:* {extra or ''}\n\n"
        "Подтвердить оформление заказа?"
    )
    await update.message.reply_text(summary, reply_markup=order_confirm_keyboard(), parse_mode="Markdown")
    return ORDER_CONFIRM

async def handle_order_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    
    if query.data != "order:confirm":
        await query.message.reply_text("Заказ отменён.")
        log_message(user, "Заказ отменён", "order_cancel")
        return ConversationHandler.END
    
    order = context.user_data.get("order", {})
    now = datetime.utcnow()
    date_part = now.strftime("%Y%m%d")
    counter = len(list(ORDERS_DIR.glob(f"ART-{date_part}-*.yaml"))) + 1
    order_id = f"ART-{date_part}-{counter:03d}"
    
    final_order = {
        "order_id": order_id,
        "timestamp": now.isoformat(),
        "user": {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
        "type": order.get("type"),
        "style": order.get("style"),
        "deadline": order.get("deadline"),
        "extra": order.get("extra"),
        "status": "confirmed",
    }
    
    path = ORDERS_DIR / f"{order_id}.yaml"
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(final_order, f, allow_unicode=True, default_flow_style=False)
    
    # Сохранение заказа в базу данных
    db.create_order(order_id, user.id, order, str(path))
    
    log_event("order_confirmed", user=user, payload={"order_id": order_id})
    log_message(user, f"Заказ оформлен: {order_id}", "order_complete")
    
    # Уведомление админа
    admin_msg = (
        f" Новый заказ!\n\nID: `{order_id}`\n"
        f"Клиент: @{user.username or user.id}\n"
        f"Тип: {order.get('type')}\nСтиль: {order.get('style')}"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg, parse_mode="Markdown")
    
    # Ответ клиенту
    client_msg = (
        f" Заказ оформлен!\n\n **{order_id}**\n"
        f" Сроки: {order.get('deadline', {}).get('raw', 'уточним')}\n\n"
        f"Свяжемся с вами скоро. Спасибо!"
    )
    await query.message.reply_text(client_msg, parse_mode="Markdown")
    
    return ConversationHandler.END

# ========================================
# Admin Commands
# ========================================
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика бота (только для админа)"""
    user = update.effective_user
    
    if user.id != ADMIN_CHAT_ID:
        await update.message.reply_text(" Доступ только для администратора")
        return
    
    stats = db.get_stats()
    
    await update.message.reply_text(
        f" **СТАТИСТИКА БОТА**\n\n"
        f" Пользователей: {stats['total_users']}\n"
        f" Сообщений: {stats['total_messages']} / {stats['messages_limit']}\n"
        f" Заказов: {stats['total_orders']}\n"
        f" Подтверждено: {stats['confirmed_orders']}\n"
        f" Заполнение базы: {stats['messages_usage_percent']}%",
        parse_mode="Markdown"
    )

# ========================================
# Основная функция
# ========================================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    order_conversation = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_order_fsm, pattern=r"^menu:new_order$")],
        states={
            ORDER_TYPE: [CallbackQueryHandler(order_type_selected, pattern=r"^order:type:")],
            ORDER_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order_style)],
            ORDER_DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order_deadline)],
            ORDER_EXTRA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order_extra)],
            ORDER_CONFIRM: [CallbackQueryHandler(handle_order_confirm, pattern=r"^order:confirm$")],
        },
        fallbacks=[
            CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern=r"^order:cancel$"),
            CommandHandler("cancel", lambda u, c: ConversationHandler.END),
        ],
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CallbackQueryHandler(on_menu_click, pattern=r"^menu:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_status_check))
    app.add_handler(order_conversation)
    
    logger.info(" MindForge Bot v3.0 запущен (с базой данных)")
    app.run_polling()

if __name__ == "__main__":
    main()
