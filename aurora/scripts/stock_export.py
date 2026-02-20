# ========================================
# Название: Stock Export
# Описание: Подготовка метаданных для стоков
# Версия: 1.0.0
# ========================================

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class StockExporter:
    """Экспорт метаданных для Adobe Stock / Shutterstock"""
    
    def __init__(self, input_folder, output_file):
        self.input_folder = input_folder
        self.output_file = output_file
    
    def export(self, keywords=None, category="People"):
        """Экспорт метаданных"""
        images = [f for f in os.listdir(self.input_folder) if f.endswith('.png')]
        
        print("=" * 60)
        print(" ЭКСПОРТ ДЛЯ СТОКОВ")
        print("=" * 60)
        print(f" Изображений: {len(images)}")
        print(f" Категория: {category}")
        print("=" * 60)
        
        default_keywords = [
            "business", "portrait", "professional", "woman",
            "corporate", "elegant", "studio", "headshot"
        ]
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_images": len(images),
            "platform": "Adobe Stock / Shutterstock",
            "category": category,
            "images": []
        }
        
        for i, img in enumerate(images):
            export_data["images"].append({
                "filename": img,
                "title": f"Professional Business Portrait {i+1}",
                "keywords": keywords or default_keywords,
                "category": category,
                "resolution": "2048x2048",
                "format": "PNG"
            })
        
        with open(self.output_file, 'w', encoding='utf8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f" Экспорт завершён")
        print(f" Отчёт: {self.output_file}")
        print("=" * 60)
        
        return export_data


if __name__ == "__main__":
    exporter = StockExporter(
        input_folder="aurora/output/upscaled_2048",
        output_file="aurora/output/stock_export/stock_metadata.json"
    )
    exporter.export()
