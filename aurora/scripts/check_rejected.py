# ========================================
# Название: Проверка бракованного изображения
# Описание: Детальный анализ portrait_00005_.png
# Версия: 1.0.0
# ========================================

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from aurora.services.quality_checker import QualityChecker

# Путь к бракованному изображению
image_path = 'aurora/output/batch_50/portrait_00005_.png'

print('=' * 60)
print(' АНАЛИЗ ОТБРАКОВАННОГО ИЗОБРАЖЕНИЯ')
print('=' * 60)
print(f' Файл: {image_path}')
print(f' Существует: {os.path.exists(image_path)}')

if not os.path.exists(image_path):
    print(' Файл не найден!')
    sys.exit(1)

checker = QualityChecker()
result = checker.evaluate(image_path)

print('=' * 60)
print(' РЕЗУЛЬТАТЫ ОЦЕНКИ')
print('=' * 60)
print(f' Общий score: {result["score"]}')
print(f' Прошло контроль: {result["passed"]}')
print('=' * 60)
print(' ДЕТАЛИ:')
print(f'  Sharpness (резкость): {result["details"]["sharpness"]}')
print(f'  Brightness (яркость): {result["details"]["brightness"]}')
print(f'  Resolution (разрешение): {result["details"]["resolution"]}')
print('=' * 60)

# Анализ причин отбраковки
print(' ПРИЧИНЫ ОТБРАКОВКИ:')

if result["details"]["sharpness"] < 0.3:
    print('    Низкая резкость (размытое изображение)')

if result["details"]["brightness"] < 0.2:
    print('    Слишком тёмное изображение')

if result["details"]["brightness"] > 0.8:
    print('    Слишком светлое изображение')

if result["details"]["resolution"] == 'FAIL':
    print('    Недостаточное разрешение')

if result["score"] >= 0.7 and result["passed"]:
    print('   Изображение прошло контроль качества')

print('=' * 60)
