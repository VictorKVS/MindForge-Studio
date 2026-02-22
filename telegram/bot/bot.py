import os
import yaml
import logging
from pathlib import Path
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler
from dotenv import load_dotenv
from database.db import get_database

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "logs"
ORDERS_DIR = BASE_DIR / "orders" / "incoming"
UPLOADS_DIR = BASE_DIR / "uploads"
LOG_DIR.mkdir(exist_ok=True)
ORDERS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", handlers=[logging.FileHandler(LOG_DIR / "bot.log", encoding="utf-8"), logging.StreamHandler()])
logger = logging.getLogger("tg-order-bot")

load_dotenv(dotenv_path=BASE_DIR / "config.env")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

if not BOT_TOKEN:
    logger.error("BOT_TOKEN не найден!")
    raise ValueError("BOT_TOKEN не найден!")
logger.info(f"BOT_TOKEN загружен: {BOT_TOKEN[:20]}...")

db = get_database()
LANGUAGE_SELECT, ORDER_TYPE, ORDER_STYLE, ORDER_DEADLINE, ORDER_EXTRA, ORDER_FILE, ORDER_CONFIRM = range(7)

TEXTS = {
    "ru": {
        "welcome": " ART STUDIO\n\nИндивидуальные визуальные работы\n\nВыберите действие:",
        "lang_select": " Выберите язык / Select language:",
        "packages": " **ПАКЕТЫ**\n\n Стандарт  от 500\n Премиум  от 2000\n Эксклюзив  индивидуально",
        "contact": " **КОНТАКТЫ**\n\nАдмин: @your_admin_username\nEmail: support@mindforge.studio",
        "status_req": " Введите номер заказа (ART-YYYYMMDD-XXX):",
        "status_found": " **Статус заказа**\n\n {order_id}\n {type}\n {style}\n {deadline}\n **{status}**",
        "status_not_found": " Заказ {order_id} не найден",
        "order_start": " **Оформление заказа**\n\n @{username}\n {time}\n\n Тип заказа:",
        "type_selected": " Выбрано: *{type}*\n\n Стиль:",
        "style_received": " Стиль: *{style}*\n\n Сроки:",
        "deadline_received": " Сроки: *{deadline}*\n\n Пожелания (или нет):",
        "extra_received": " Пожелания сохранены\n\n **Загрузить фото?**\n\n Пример позы\n Референс эмоции\n Групповое фото\n\n 152-ФЗ: загрузка = согласие на обработку данных",
        "confirm_summary": " **Подтверждение**\n\n Тип: {type}\n Стиль: {style}\n Сроки: {deadline}\n Пожелания: {extra}\n Файл: {file}",
        "confirmed": " **Заказ оформлен!**\n\n **{order_id}**\n Сроки: {deadline}\n В базу записано\n 152-ФЗ: согласие зафиксировано",
        "cancelled": " Отменено",
        "file_uploaded": " Фото загружено!\n\n {filename}\n {size} байт",
        "file_invalid": " Загрузите изображение (PNG, JPG, JPEG)",
        "my_stats": " **Ваша статистика**\n\n Сообщений: {messages}\n Заказов: {orders}",
        "btn_new": " Новый заказ",
        "btn_packages": " Пакеты",
        "btn_status": " Статус",
        "btn_contact": " Контакт",
        "btn_lang": " Язык",
        "btn_stats": " Моя статистика",
        "btn_single": " Одно изображение",
        "btn_series": " Серия работ",
        "btn_consult": " Консультация",
        "btn_confirm": " Подтвердить",
        "btn_edit": " Изменить",
        "btn_cancel": " Отменить",
        "btn_upload": " Загрузить фото",
        "btn_skip": " Пропустить",
        "btn_back": " Назад",
        "btn_home": " В начало",
        "btn_ru": " Русский",
        "btn_en": " English",
    },
    "en": {
        "welcome": " ART STUDIO\n\nIndividual visual works\n\nSelect action:",
        "lang_select": " Выберите язык / Select language:",
        "packages": " **PACKAGES**\n\n Standard  from 500\n Premium  from 2000\n Exclusive  individual",
        "contact": " **CONTACTS**\n\nAdmin: @your_admin_username\nEmail: support@mindforge.studio",
        "status_req": " Enter order number (ART-YYYYMMDD-XXX):",
        "status_found": " **Order Status**\n\n {order_id}\n {type}\n {style}\n {deadline}\n **{status}**",
        "status_not_found": " Order {order_id} not found",
        "order_start": " **Order Placement**\n\n @{username}\n {time}\n\n Order type:",
        "type_selected": " Selected: *{type}*\n\n Style:",
        "style_received": " Style: *{style}*\n\n Deadline:",
        "deadline_received": " Deadline: *{deadline}*\n\n Notes (or no):",
        "extra_received": " Notes saved\n\n **Upload photo?**\n\n Pose example\n Emotion reference\n Group photo\n\n 152-FZ: upload = data processing consent",
        "confirm_summary": " **Confirmation**\n\n Type: {type}\n Style: {style}\n Deadline: {deadline}\n Notes: {extra}\n File: {file}",
        "confirmed": " **Order Confirmed!**\n\n **{order_id}**\n Deadline: {deadline}\n Logged to database\n 152-FZ: consent recorded",
        "cancelled": " Cancelled",
        "file_uploaded": " Photo uploaded!\n\n {filename}\n {size} bytes",
        "file_invalid": " Upload image (PNG, JPG, JPEG)",
        "my_stats": " **Your Stats**\n\n Messages: {messages}\n Orders: {orders}",
        "btn_new": " New Order",
        "btn_packages": " Packages",
        "btn_status": " Status",
        "btn_contact": " Contact",
        "btn_lang": " Language",
        "btn_stats": " My Stats",
        "btn_single": " Single Image",
        "btn_series": " Series",
        "btn_consult": " Consultation",
        "btn_confirm": " Confirm",
        "btn_edit": " Edit",
        "btn_cancel": " Cancel",
        "btn_upload": " Upload Photo",
        "btn_skip": " Skip",
        "btn_back": " Back",
        "btn_home": " Home",
        "btn_ru": " Русский",
        "btn_en": " English",
    }
}

def get_text(lang, key):
    return TEXTS.get(lang, TEXTS["ru"]).get(key, "")

def build_keyboard(buttons):
    if not buttons:
        return None
    return InlineKeyboardMarkup([[InlineKeyboardButton(str(text), callback_data=str(data)) for text, data in row] for row in buttons if row])

def build_keyboard_with_nav(buttons, show_home=True, show_back=False, lang="ru"):
    if buttons is None:
        buttons = []
    nav_row = []
    if show_back:
        nav_row.append((get_text(lang, "btn_back"), "nav:back"))
    if show_home:
        nav_row.append((get_text(lang, "btn_home"), "nav:home"))
    if nav_row:
        buttons.append(nav_row)
    return build_keyboard(buttons)

def main_menu_keyboard(lang="ru"):
    return build_keyboard([
        [(get_text(lang, "btn_new"), "menu:new_order")],
        [(get_text(lang, "btn_packages"), "menu:packages")],
        [(get_text(lang, "btn_status"), "menu:status")],
        [(get_text(lang, "btn_contact"), "menu:contact")],
        [(get_text(lang, "btn_stats"), "menu:mystats")],
        [(get_text(lang, "btn_lang"), "menu:language")],
    ])

def language_keyboard(lang="ru"):
    return build_keyboard([
        [(get_text("ru", "btn_ru"), "lang:ru")],
        [(get_text("en", "btn_en"), "lang:en")],
        [(get_text(lang, "btn_back"), "nav:back")],
    ])

def order_type_keyboard(lang="ru"):
    return build_keyboard_with_nav([
        [(get_text(lang, "btn_single"), "order:type:single")],
        [(get_text(lang, "btn_series"), "order:type:series")],
        [(get_text(lang, "btn_consult"), "order:type:consult")],
    ], show_home=True, show_back=True, lang=lang)

def order_confirm_keyboard(lang="ru"):
    return build_keyboard_with_nav([
        [(get_text(lang, "btn_confirm"), "order:confirm")],
        [(get_text(lang, "btn_edit"), "order:edit")],
        [(get_text(lang, "btn_cancel"), "order:cancel")],
    ], show_home=True, show_back=True, lang=lang)

def file_upload_keyboard(lang="ru"):
    return build_keyboard_with_nav([
        [(get_text(lang, "btn_upload"), "order:file:upload")],
        [(get_text(lang, "btn_skip"), "order:file:skip")],
    ], show_home=True, show_back=True, lang=lang)

def log_event(event_type, user=None, payload=None):
    data = {"event": event_type, "timestamp": datetime.utcnow().isoformat()}
    if user:
        data["user"] = {"id": user.id, "username": user.username}
    if payload:
        data.update(payload)
    logger.info(f"[{event_type}] {data}")
    if user:
        db.log_event(event_type, user.id, payload or {})

def log_message(user, message_text: str, message_type: str):
    db.log_message(user_id=user.id, message_text=message_text, message_type=message_type, chat_id=user.id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = context.user_data.get("lang", "ru")
    db.upsert_user(user.id, user.username, user.first_name, user.last_name)
    log_event("start", user=user)
    log_message(user, "/start", "command")
    if "lang" not in context.user_data:
        await update.message.reply_text(get_text(lang, "lang_select"), reply_markup=language_keyboard(lang))
    else:
        await update.message.reply_text(get_text(lang, "welcome"), reply_markup=main_menu_keyboard(lang))

async def on_menu_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data
    lang = context.user_data.get("lang", "ru")
    log_event("menu_click", user=user, payload={"action": data})
    log_message(user, f"Button: {data}", "callback")
    
    if data == "nav:home" or data == "nav:back":
        await query.message.edit_text(get_text(lang, "welcome"), reply_markup=main_menu_keyboard(lang))
        return
    if data == "menu:language":
        await query.message.reply_text(get_text(lang, "lang_select"), reply_markup=language_keyboard(lang))
        return
    if data.startswith("lang:"):
        new_lang = data.split(":")[1]
        context.user_data["lang"] = new_lang
        await query.message.edit_text(f" Language: {get_text(new_lang, 'btn_ru') if new_lang == 'ru' else get_text(new_lang, 'btn_en')}", reply_markup=main_menu_keyboard(new_lang))
        return
    if data == "menu:new_order":
        return await start_order_fsm(update, context)
    elif data == "menu:packages":
        await query.message.reply_text(get_text(lang, "packages"), reply_markup=build_keyboard_with_nav([], show_home=True, lang=lang), parse_mode="Markdown")
    elif data == "menu:status":
        await query.message.reply_text(get_text(lang, "status_req"), reply_markup=build_keyboard_with_nav([], show_home=True, lang=lang), parse_mode="Markdown")
        context.user_data["awaiting_status"] = True
    elif data == "menu:contact":
        await query.message.reply_text(get_text(lang, "contact"), reply_markup=build_keyboard_with_nav([], show_home=True, lang=lang), parse_mode="Markdown")
    elif data == "menu:mystats":
        stats = db.get_user_stats(user.id)
        await query.message.reply_text(get_text(lang, "my_stats").format(messages=stats['total_messages'], orders=stats['total_orders']), reply_markup=build_keyboard_with_nav([], show_home=True, lang=lang), parse_mode="Markdown")

async def handle_status_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    lang = context.user_data.get("lang", "ru")
    log_message(user, text, "text")
    if context.user_data.get("awaiting_status"):
        if not text.startswith("ART-"):
            await update.message.reply_text(get_text(lang, "status_not_found").format(order_id=text), reply_markup=build_keyboard_with_nav([], show_home=True, lang=lang))
            return
        order = db.get_order(text)
        if order:
            await update.message.reply_text(get_text(lang, "status_found").format(**order), reply_markup=build_keyboard_with_nav([], show_home=True, lang=lang), parse_mode="Markdown")
        else:
            await update.message.reply_text(get_text(lang, "status_not_found").format(order_id=text), reply_markup=build_keyboard_with_nav([], show_home=True, lang=lang))
        context.user_data["awaiting_status"] = False

async def start_order_fsm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang = context.user_data.get("lang", "ru")
    context.user_data["order"] = {}
    log_event("order_start", user=user)
    log_message(user, "Started order", "order_start")
    await query.message.reply_text(get_text(lang, "order_start").format(username=user.username or user.id, time=datetime.now().strftime("%H:%M:%S")), reply_markup=order_type_keyboard(lang), parse_mode="Markdown")
    return ORDER_TYPE

async def order_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang = context.user_data.get("lang", "ru")
    order_type = query.data.split(":", 2)[2]
    type_map = {"single": get_text(lang, "btn_single"), "series": get_text(lang, "btn_series"), "consult": get_text(lang, "btn_consult")}
    context.user_data["order"]["type"] = type_map[order_type]
    log_event("type_selected", user=user, payload={"type": type_map[order_type]})
    log_message(user, f"Type: {type_map[order_type]}", "order_step")
    await query.message.reply_text(get_text(lang, "type_selected").format(type=type_map[order_type]), reply_markup=build_keyboard_with_nav([], show_home=True, show_back=True, lang=lang), parse_mode="Markdown")
    return ORDER_STYLE

async def handle_order_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    lang = context.user_data.get("lang", "ru")
    style = update.message.text.strip()
    context.user_data["order"]["style"] = style
    log_event("style_received", user=user, payload={"style": style})
    log_message(user, f"Style: {style}", "order_step")
    await update.message.reply_text(get_text(lang, "style_received").format(style=style), reply_markup=build_keyboard_with_nav([], show_home=True, show_back=True, lang=lang), parse_mode="Markdown")
    return ORDER_DEADLINE

async def handle_order_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    lang = context.user_data.get("lang", "ru")
    deadline = update.message.text.strip()
    context.user_data["order"]["deadline"] = {"raw": deadline}
    log_event("deadline_received", user=user, payload={"deadline": deadline})
    log_message(user, f"Deadline: {deadline}", "order_step")
    await update.message.reply_text(get_text(lang, "deadline_received").format(deadline=deadline), reply_markup=build_keyboard_with_nav([], show_home=True, show_back=True, lang=lang), parse_mode="Markdown")
    return ORDER_EXTRA

async def handle_order_extra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    lang = context.user_data.get("lang", "ru")
    text = update.message.text.strip()
    extra = None if text.lower() in ("нет", "no", "none", "-") else text
    context.user_data["order"]["extra"] = extra
    log_event("extra_received", user=user, payload={"extra": extra})
    log_message(user, f"Extra: {extra or 'None'}", "order_step")
    await update.message.reply_text(get_text(lang, "extra_received"), reply_markup=file_upload_keyboard(lang), parse_mode="Markdown")
    return ORDER_FILE

async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = context.user_data.get("lang", "ru")
    if update.message.photo:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_path = UPLOADS_DIR / f"{user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"
        await file.download_to_drive(file_path)
        context.user_data["order"]["file_path"] = str(file_path)
        log_event("file_uploaded", user=user, payload={"file": str(file_path)})
        log_message(user, f"Photo: {file_path.name}", "file_upload")
        await update.message.reply_text(get_text(lang, "file_uploaded").format(filename=file_path.name, size=photo.file_size), reply_markup=order_confirm_keyboard(lang))
        return ORDER_CONFIRM
    elif update.message.document:
        doc = update.message.document
        if not doc.mime_type.startswith('image/'):
            await update.message.reply_text(get_text(lang, "file_invalid"), reply_markup=file_upload_keyboard(lang))
            return ORDER_FILE
        file = await context.bot.get_file(doc.file_id)
        file_path = UPLOADS_DIR / f"{user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{doc.file_name}"
        await file.download_to_drive(file_path)
        context.user_data["order"]["file_path"] = str(file_path)
        log_event("file_uploaded", user=user, payload={"file": str(file_path)})
        log_message(user, f"File: {file_path.name}", "file_upload")
        await update.message.reply_text(get_text(lang, "file_uploaded").format(filename=file_path.name, size=doc.file_size), reply_markup=order_confirm_keyboard(lang))
        return ORDER_CONFIRM
    return ORDER_FILE

async def handle_order_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang = context.user_data.get("lang", "ru")
    if query.data == "order:cancel":
        await query.message.reply_text(get_text(lang, "cancelled"), reply_markup=build_keyboard_with_nav([], show_home=True, lang=lang))
        log_event("order_cancelled", user=user)
        log_message(user, "Order cancelled", "order_cancel")
        return ConversationHandler.END
    if query.data == "order:edit":
        await query.message.reply_text(" Restart order:")
        return ConversationHandler.END
    order = context.user_data.get("order", {})
    now = datetime.utcnow()
    date_part = now.strftime("%Y%m%d")
    counter = len(list(ORDERS_DIR.glob(f"ART-{date_part}-*.yaml"))) + 1
    order_id = f"ART-{date_part}-{counter:03d}"
    final_order = {
        "order_id": order_id,
        "timestamp": now.isoformat(),
        "user": {"id": user.id, "username": user.username, "first_name": user.first_name, "last_name": user.last_name},
        "type": order.get("type"),
        "style": order.get("style"),
        "deadline": order.get("deadline"),
        "extra": order.get("extra"),
        "file_path": order.get("file_path"),
        "status": "confirmed",
        "language": lang,
        "legal": {"152fz_accepted": True, "accepted_at": now.isoformat()}
    }
    path = ORDERS_DIR / f"{order_id}.yaml"
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(final_order, f, allow_unicode=True, default_flow_style=False)
    db.create_order(order_id, user.id, order, str(path), lang)
    log_event("order_confirmed", user=user, payload={"order_id": order_id})
    log_message(user, f"Order: {order_id}", "order_complete")
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f" Заказ {order_id}\nКлиент: @{user.username or user.id}\nЯзык: {lang}")
    await query.message.reply_text(get_text(lang, "confirmed").format(order_id=order_id, deadline=order.get('deadline', {}).get('raw', 'уточним')), reply_markup=build_keyboard_with_nav([], show_home=True, lang=lang), parse_mode="Markdown")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    order_conversation = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_order_fsm, pattern=r"^menu:new_order$")],
        states={
            ORDER_TYPE: [CallbackQueryHandler(order_type_selected, pattern=r"^order:type:")],
            ORDER_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order_style)],
            ORDER_DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order_deadline)],
            ORDER_EXTRA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order_extra)],
            ORDER_FILE: [
                MessageHandler(filters.PHOTO | filters.Document.ALL, handle_file_upload),
                CallbackQueryHandler(handle_order_confirm, pattern=r"^order:(file|confirm|edit|cancel):")
            ],
            ORDER_CONFIRM: [CallbackQueryHandler(handle_order_confirm, pattern=r"^order:(confirm|edit|cancel)$")],
        },
        fallbacks=[CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern=r"^order:cancel$")],
        per_message=True,
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_menu_click, pattern=r"^menu:"))
    app.add_handler(CallbackQueryHandler(on_menu_click, pattern=r"^lang:"))
    app.add_handler(CallbackQueryHandler(on_menu_click, pattern=r"^nav:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_status_check))
    app.add_handler(order_conversation)
    logger.info(" Bot v7.0 запущен (Multi-Language + DB + Photo + Navigation + 152-FZ)")
    app.run_polling()

if __name__ == "__main__":
    main()
