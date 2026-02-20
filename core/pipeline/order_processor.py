# ========================================
# Название: Order Processor
# Описание: Обработка YAML заказов
# Версия: 1.0.0
# ========================================

import sys
import os
import yaml

# Добавляем корень проекта в путь (2 уровня вверх)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.agents.art_director import ArtDirectorAgent

class OrderProcessor:
    """Обработка заказов из YAML"""
    
    def __init__(self):
        self.art_director = ArtDirectorAgent()
    
    def load_order(self, order_path):
        """Загрузка заказа из YAML"""
        if not os.path.exists(order_path):
            raise FileNotFoundError(f"Заказ не найден: {order_path}")
        
        with open(order_path, 'r', encoding='utf8') as f:
            return yaml.safe_load(f)
    
    def process_image_order(self, order):
        """Обработка заказа на изображения"""
        print("=" * 60)
        print(" ОБРАБОТКА ЗАКАЗА НА ИЗОБРАЖЕНИЯ")
        print("=" * 60)
        
        content = order.get("content", {})
        technical = order.get("technical", {})
        quality = order.get("quality", {})
        
        # Сборка промпта через Art Director
        prompt_config = self.art_director.assemble_prompt({
            "style": content.get("style", "business"),
            "emotion": content.get("emotion", "neutral"),
            "pose": content.get("pose", "front_facing"),
            "lighting": content.get("lighting", "studio"),
            "subject": content.get("subject", "portrait")
        })
        
        print(f" Prompt: {prompt_config['prompt'][:100]}...")
        print(f" Negative: {prompt_config['negative'][:50]}...")
        print(f"  CFG: {prompt_config['cfg']}, Steps: {prompt_config['steps']}")
        print(f" Resolution: {prompt_config['resolution']}")
        print(f" Count: {technical.get('count', 1)}")
        print(f" Min Score: {quality.get('min_score', 0.7)}")
        print("=" * 60)
        
        return {
            "prompt": prompt_config["prompt"],
            "negative": prompt_config["negative"],
            "count": technical.get("count", 1),
            "resolution": prompt_config["resolution"],
            "steps": prompt_config["steps"],
            "cfg": prompt_config["cfg"],
            "min_score": quality.get("min_score", 0.7)
        }
    
    def process_website_order(self, order):
        """Обработка заказа на сайт"""
        print("=" * 60)
        print(" ОБРАБОТКА ЗАКАЗА НА САЙТ")
        print("=" * 60)
        
        website = order.get("website", {})
        content = website.get("content", {})
        visual = order.get("visual", {})
        
        print(f" Ниша: {website.get('niche', 'general')}")
        print(f" Стиль: {website.get('style', 'clean')}")
        print(f" Страниц: {len(website.get('pages', []))}")
        print(f" Hero: {content.get('hero', {}).get('headline', 'N/A')[:50]}...")
        print(f" Цвета: {visual.get('color_scheme', 'default')}")
        print(f" Layout: {visual.get('layout', 'grid')}")
        print("=" * 60)
        
        return {
            "niche": website.get("niche", "general"),
            "pages": website.get("pages", []),
            "hero": content.get("hero", {}),
            "sections": content.get("sections", []),
            "color_scheme": visual.get("color_scheme", "default"),
            "layout": visual.get("layout", "grid")
        }


if __name__ == "__main__":
    processor = OrderProcessor()
    
    # Тест заказа на изображения
    print("\n ТЕСТ 1: Заказ на изображения")
    image_order_path = "orders/images/stock_portrait_001.yaml"
    if os.path.exists(image_order_path):
        image_order = processor.load_order(image_order_path)
        processor.process_image_order(image_order)
    else:
        print(f"  Файл не найден: {image_order_path}")
    
    # Тест заказа на сайт
    print("\n ТЕСТ 2: Заказ на сайт")
    web_order_path = "orders/websites/medical_clinic_001.yaml"
    if os.path.exists(web_order_path):
        web_order = processor.load_order(web_order_path)
        processor.process_website_order(web_order)
    else:
        print(f"  Файл не найден: {web_order_path}")
