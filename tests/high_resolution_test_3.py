import sys
sys.path.insert(0, '.')
from core.adapters.comfyui import ComfyUIAdapter
import time
import os

print("="*60)
print(" ТЕСТ: ГЕНЕРАЦИЯ НА ВЫСОКОМ РАЗРЕШЕНИИ (384x384)")
print(" Качество: high (384x384, 10 шагов, CFG 6.0)")
print("="*60)

adapter = ComfyUIAdapter()
if not adapter.health_check():
    print(" ComfyUI не запущен")
    sys.exit(1)
print(" ComfyUI запущен")

# Очищаем папку
batch_dir = r"G:\1\AI\ComfyUI\ComfyUI\output\batch"
for f in os.listdir(batch_dir):
    if f.endswith('.png'):
        os.remove(os.path.join(batch_dir, f))
print(" Папка очищена")

# Проверка на 3 генерации
success = 0
for i in range(3):
    print(f"\n{'='*60}")
    print(f"  Генерация #{i+1}/3")
    print(f"{'='*60}")
    
    try:
        start = time.time()
        result = adapter.generate(
            prompt="professional portrait woman, perfect facial proportions, symmetrical face",
            negative="ugly, blurry, deformed face, bad anatomy, distorted features, asymmetrical face, bad proportions",
            quality="high",
            seed=1000 + i
        )
        elapsed = time.time() - start
        success += 1
        print(f" Успех за {elapsed:.1f} сек | {os.path.basename(result['image_path'])}")
    except Exception as e:
        print(f" Падение на генерации #{i+1}: {e}")
        break

print("\n" + "="*60)
print(f" Успешно: {success}/3")
print("="*60)
