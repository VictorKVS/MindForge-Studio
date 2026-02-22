# ========================================
# Telegram Order Pipeline
# Полный пайплайн: Telegram  Генерация  Доставка
# ========================================

import sys
import os
import yaml
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bridge import TelegramToMindForgeBridge

class TelegramOrderPipeline:
    def __init__(self):
        self.bridge = TelegramToMindForgeBridge(
            telegram_orders_dir="telegram/bot/orders/incoming",
            studio_orders_dir="orders/telegram"
        )
    
    def process_telegram_order(self, order_id):
        order_path = Path(f"orders/telegram/{order_id}.yaml")
        
        if not order_path.exists():
            return {"error": f"Заказ не найден: {order_id}"}
        
        with open(order_path, 'r', encoding='utf-8') as f:
            order = yaml.safe_load(f)
        
        print("=" * 60)
        print(f" ОБРАБОТКА ЗАКАЗА: {order_id}")
        print("=" * 60)
        
        return {
            "order_id": order_id,
            "status": "processing",
            "user_id": order.get('_telegram', {}).get('user', {}).get('id')
        }
    
    def run(self):
        converted = self.bridge.process_pending_orders()
        for order_path in converted:
            order_id = order_path.stem
            self.process_telegram_order(order_id)


if __name__ == "__main__":
    pipeline = TelegramOrderPipeline()
    pipeline.run()
