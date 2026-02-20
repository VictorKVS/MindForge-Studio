# ========================================
# Название: Quality Checker
# Описание: Оценка качества изображений
# Версия: 1.1.0 (Исправлен min_resolution)
# ========================================

import os
import json
from datetime import datetime
from PIL import Image
import numpy as np

class QualityChecker:
    """
    Автоматическая оценка качества изображений.
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        # Устанавливаем значения по умолчанию
        self.min_resolution = self.config.get("min_resolution", 512)
        self.min_sharpness = self.config.get("min_sharpness", 0.3)
        self.min_brightness = self.config.get("min_brightness", 0.2)
        self.max_brightness = self.config.get("max_brightness", 0.8)
        self.min_quality_score = self.config.get("min_quality_score", 0.7)
    
    def check_blur(self, image_path):
        """Проверка на размытость"""
        try:
            img = Image.open(image_path).convert('L')
            img_np = np.array(img)
            variance = np.var(img_np)
            sharpness = min(1.0, variance / 500)
            return sharpness
        except Exception as e:
            print(f" Ошибка проверки blur: {e}")
            return 0.0
    
    def check_brightness(self, image_path):
        """Проверка яркости"""
        try:
            img = Image.open(image_path).convert('L')
            img_np = np.array(img)
            brightness = np.mean(img_np) / 255.0
            return brightness
        except Exception as e:
            print(f" Ошибка проверки brightness: {e}")
            return 0.5
    
    def check_resolution(self, image_path):
        """Проверка разрешения"""
        try:
            img = Image.open(image_path)
            width, height = img.size
            min_side = min(width, height)
            return min_side >= self.min_resolution
        except Exception as e:
            print(f" Ошибка проверки resolution: {e}")
            return False
    
    def evaluate(self, image_path):
        """Полная оценка изображения"""
        if not os.path.exists(image_path):
            return {
                "score": 0.0,
                "passed": False,
                "details": {"error": "File not found"}
            }
        
        sharpness = self.check_blur(image_path)
        brightness = self.check_brightness(image_path)
        resolution_ok = self.check_resolution(image_path)
        
        # Расчёт общего score
        score = 0.0
        score += sharpness * 0.4
        score += (1.0 - abs(brightness - 0.5)) * 0.3
        score += 0.3 if resolution_ok else 0.0
        
        passed = (
            score >= self.min_quality_score and
            sharpness >= self.min_sharpness and
            self.min_brightness <= brightness <= self.max_brightness and
            resolution_ok
        )
        
        return {
            "score": round(score, 3),
            "passed": passed,
            "details": {
                "sharpness": round(sharpness, 3),
                "brightness": round(brightness, 3),
                "resolution": "OK" if resolution_ok else "FAIL"
            }
        }
    
    def save_report(self, image_path, result, report_folder="aurora/output/quality_reports"):
        """Сохранение отчёта о качестве"""
        os.makedirs(report_folder, exist_ok=True)
        
        report = {
            "image": os.path.basename(image_path),
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        
        report_path = os.path.join(
            report_folder,
            f"{os.path.splitext(os.path.basename(image_path))[0]}_quality.json"
        )
        
        with open(report_path, 'w', encoding='utf8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report_path
