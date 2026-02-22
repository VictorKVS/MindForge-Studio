# ========================================
# Название: Проверка разрешения изображений
# Описание: Анализ всех изображений в папке
# ========================================

import sys
import os
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

folder = 'aurora/output/batch_50'
images = [f for f in os.listdir(folder) if f.endswith('.png')]

print('=' * 60)
print(' ПРОВЕРКА РАЗРЕШЕНИЯ ВСЕХ ИЗОБРАЖЕНИЙ')
print('=' * 60)

below_512 = []
ok_512 = []

for img in images:
    path = os.path.join(folder, img)
    try:
        image = Image.open(path)
        width, height = image.size
        min_side = min(width, height)
        
        if min_side >= 512:
            ok_512.append((img, width, height))
        else:
            below_512.append((img, width, height))
            print(f' {img}: {width}x{height} (меньше 512px)')
    except Exception as e:
        print(f'  {img}: Ошибка чтения - {e}')

print('=' * 60)
print(f' В норме (>= 512px): {len(ok_512)}')
print(f' Ниже нормы (< 512px): {len(below_512)}')
print('=' * 60)

if below_512:
    print('\n Список изображений с низким разрешением:')
    for img, w, h in below_512:
        print(f'   - {img}: {w}x{h}')
