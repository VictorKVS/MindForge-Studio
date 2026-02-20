# ========================================
# Название: Тест Quality Checker
# Описание: Проверка качества изображений
# Версия: 1.1.0 (Исправлены пути и ошибки)
# ========================================

import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from aurora.services.quality_checker import QualityChecker

# Проверяем существование папки
folder = 'aurora/output/batch_50'
full_path = os.path.abspath(folder)

print('=' * 60)
print(' ТЕСТ QUALITY CHECKER')
print('=' * 60)
print(f' Путь к папке: {full_path}')
print(f' Папка существует: {os.path.exists(folder)}')

if not os.path.exists(folder):
    print(' Папка не найдена!')
    sys.exit(1)

# Ищем PNG файлы
images = [f for f in os.listdir(folder) if f.endswith('.png')]
print(f' Найдено изображений: {len(images)}')

if len(images) == 0:
    print('  PNG файлы не найдены в папке')
    print(' Содержимое папки:')
    for f in os.listdir(folder):
        print(f'   - {f}')
    sys.exit(0)

print('=' * 60)

passed = 0
failed = 0

# Тестируем первые 10 изображений
for img in images[:10]:
    path = os.path.join(folder, img)
    result = QualityChecker().evaluate(path)
    status = '' if result['passed'] else ''
    score = result['score']
    print(f'{status} {img}: score={score}')
    
    if result['passed']:
        passed += 1
    else:
        failed += 1

print('=' * 60)
print(f' Прошло: {passed}/{len(images[:10])}')
print(f' Отбраковано: {failed}/{len(images[:10])}')

# Защита от деления на ноль
total = len(images[:10])
if total > 0:
    percent = passed / total * 100
    print(f' Процент качества: {percent:.1f}%')
else:
    print(' Процент качества: N/A')

print('=' * 60)
