# ========================================
# MindForge Telegram Bot v5.0
# TOP-LEVEL Professional Bot (FREE STACK)
# ========================================

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler,
)
from config.settings import BOT_TOKEN
from utils.logger import logger

# Импорты handlers
from handlers.start import start_handler, menu_handler
from handlers.order import (
    start_order_fsm, order_type_selected, handle_order_style,
    handle_order_deadline, handle_order_extra, handle_file_upload,
    handle_order_confirm, ORDER_TYPE, ORDER_STYLE, ORDER_DEADLINE,
    ORDER_EXTRA, ORDER_FILE, ORDER_CONFIRM
)

def main():
    """Запуск бота"""
    logger.info("=" * 60)
    logger.info(" MindForge Bot v5.0 запускается...")
    logger.info("=" * 60)
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # FSM для заказов
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
        fallbacks=[
            CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern=r"^order:cancel$"),
        ],
    )
    
    # Handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CallbackQueryHandler(menu_handler, pattern=r"^menu:"))
    app.add_handler(CallbackQueryHandler(menu_handler, pattern=r"^nav:"))
    app.add_handler(order_conversation)
    
    logger.info(" Бот успешно запущен!")
    logger.info(" Логирование: экран + файл + база данных")
    logger.info(" 152-ФЗ: предупреждение и согласие")
    logger.info(" База данных: SQLite (10,000 сообщений)")
    logger.info("=" * 60)
    
    app.run_polling()

if __name__ == "__main__":
    main()
