# ========================================
# Название: Авто-сортировка по качеству
# Описание: Перемещение бракованных в rejected/
# Версия: 1.0.0
# ========================================

import sys
import os
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from aurora.services.quality_checker import QualityChecker

folder = 'aurora/output/batch_50'
rejected_folder = 'aurora/output/rejected'
os.makedirs(rejected_folder, exist_ok=True)

checker = QualityChecker()
images = [f for f in os.listdir(folder) if f.endswith('.png')]

print('=' * 60)
print(' АВТО-СОРТИРОВКА ПО КАЧЕСТВУ')
print('=' * 60)

passed = 0
rejected = 0

for img in images:
    path = os.path.join(folder, img)
    result = checker.evaluate(path)
    
    if result['passed']:
        passed += 1
    else:
        dest = os.path.join(rejected_folder, img)
        shutil.move(path, dest)
        print(f' {img}: score={result["score"]}  rejected/')
        rejected += 1

print('=' * 60)
print(f' Осталось в batch_50: {passed}')
print(f' Перемещено в rejected: {rejected}')
print('=' * 60)
