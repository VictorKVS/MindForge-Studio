# ========================================
# Telegram  MindForge Bridge
# Конвертация заказов из Telegram в формат студии
# ========================================

import os
import yaml
from pathlib import Path
from datetime import datetime

class TelegramToMindForgeBridge:
    def __init__(self, telegram_orders_dir, studio_orders_dir):
        self.telegram_orders_dir = Path(telegram_orders_dir)
        self.studio_orders_dir = Path(studio_orders_dir)
        self.processed_dir = self.telegram_orders_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)
        
        self.style_mapping = {
            "киберпанк": {"style": "artistic", "emotion": "mysterious", "lighting": "neon"},
            "фэнтези": {"style": "artistic", "emotion": "mysterious", "lighting": "dramatic"},
            "бизнес": {"style": "business", "emotion": "confidence", "lighting": "studio"},
            "портрет": {"style": "business", "emotion": "calm", "lighting": "soft"},
            "мода": {"style": "fashion", "emotion": "seductive", "lighting": "rim"},
            "кино": {"style": "cinematic", "emotion": "mysterious", "lighting": "dramatic"},
        }
    
    def convert_order(self, telegram_order_path):
        with open(telegram_order_path, 'r', encoding='utf-8') as f:
            tg_order = yaml.safe_load(f)
        
        tg_style = tg_order.get('style', '').lower()
        mapped = self.style_mapping.get('бизнес')
        for key, value in self.style_mapping.items():
            if key in tg_style:
                mapped = value
                break
        
        studio_order = {
            "order": {
                "id": tg_order.get('order_id'),
                "type": "image",
                "source": "telegram",
                "priority": "high" if tg_order.get('type') == 'Серия работ' else "normal",
                "created_at": tg_order.get('timestamp')
            },
            "content": {
                "subject": tg_order.get('style', 'portrait'),
                "style": mapped['style'],
                "emotion": mapped['emotion'],
                "pose": "three_quarter",
                "lighting": mapped['lighting'],
                "background": "neutral"
            },
            "technical": {
                "resolution": "512x512",
                "steps": 25,
                "cfg": 5.5,
                "seed": -1,
                "count": 5 if tg_order.get('type') == 'Серия работ' else 1
            },
            "quality": {
                "min_score": 0.7,
                "auto_reject": True,
                "upscale": True,
                "target_resolution": "2048x2048"
            },
            "output": {
                "folder": f"aurora/output/telegram_{tg_order.get('order_id')}",
                "format": "png",
                "metadata": True,
                "telegram_delivery": True,
                "user_id": tg_order.get('user', {}).get('id')
            },
            "_telegram": {
                "original_order": tg_order,
                "user": tg_order.get('user'),
                "deadline": tg_order.get('deadline'),
                "extra": tg_order.get('extra')
            }
        }
        
        studio_path = self.studio_orders_dir / f"{tg_order.get('order_id')}.yaml"
        with open(studio_path, 'w', encoding='utf-8') as f:
            yaml.dump(studio_order, f, allow_unicode=True, default_flow_style=False)
        
        telegram_order_path.rename(self.processed_dir / telegram_order_path.name)
        return studio_path
    
    def process_pending_orders(self):
        pending = list(self.telegram_orders_dir.glob("ART-*.yaml"))
        print("=" * 60)
        print(" TELEGRAM  MINDFORGE BRIDGE")
        print("=" * 60)
        print(f" Найдено заказов: {len(pending)}")
        
        converted = []
        for order_path in pending:
            try:
                studio_path = self.convert_order(order_path)
                print(f" {order_path.name}  {studio_path.name}")
                converted.append(studio_path)
            except Exception as e:
                print(f" {order_path.name}: {e}")
        
        print("=" * 60)
        print(f" Конвертировано: {len(converted)}")
        print("=" * 60)
        return converted


if __name__ == "__main__":
    bridge = TelegramToMindForgeBridge(
        telegram_orders_dir="telegram/bot/orders/incoming",
        studio_orders_dir="orders/telegram"
    )
    bridge.process_pending_orders()
