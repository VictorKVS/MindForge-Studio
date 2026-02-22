# ========================================
# Тест базы данных
# ========================================

from database import get_database

print("=" * 60)
print("  БАЗА ДАННЫХ  ТЕСТ")
print("=" * 60)

db = get_database()

# Проверка статистики
stats = db.get_stats()
print(f" Пользователей: {stats['total_users']}")
print(f" Сообщений: {stats['total_messages']} / {stats['messages_limit']}")
print(f" Заказов: {stats['total_orders']}")
print(f" Заполнение: {stats['messages_usage_percent']}%")
print("=" * 60)
print(" БАЗА ДАННЫХ ГОТОВА!")
print("=" * 60)
