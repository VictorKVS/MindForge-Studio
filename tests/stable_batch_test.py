import sys
sys.path.insert(0, '.')
from core.adapters.comfyui import ComfyUIAdapter
import time, os

print("="*60)
print(" ТЕСТ: 5 ГЕНЕРАЦИЙ ПОДРЯД")
print(" 448x448, 12 шагов, пауза 1 сек")
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

success = 0
for i in range(5):
    print(f"\n{'='*60}")
    print(f"  Генерация #{i+1}/5")
    print(f"{'='*60}")
    
    try:
        start = time.time()
        result = adapter.generate(
            prompt="professional portrait woman",
            negative="ugly, blurry",
            width=448,
            height=448,
            seed=100 + i
        )
        elapsed = time.time() - start
        success += 1
        print(f" Успех за {elapsed:.1f} сек | {os.path.basename(result['image_path'])}")
    except Exception as e:
        print(f" Падение на генерации #{i+1}: {e}")
        break

print("\n" + "="*60)
print(f" Успешно: {success}/5 генераций")
print("="*60)
