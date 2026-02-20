import sys
sys.path.insert(0, '.')
from core.adapters.comfyui import ComfyUIAdapter
import time, os

print("="*60)
print(" ТЕСТ СТАБИЛЬНОСТИ")
print(" 448x448, 12 шагов, пауза 3 сек")
print(" Имена: portrait_001.png, portrait_002.png...")
print("="*60)

adapter = ComfyUIAdapter()
if not adapter.health_check():
    print(" ComfyUI не запущен")
    sys.exit(1)
print(" ComfyUI запущен")

batch_dir = r"G:\1\AI\ComfyUI\ComfyUI\output\batch"
for f in os.listdir(batch_dir):
    if f.endswith('.png'):
        os.remove(os.path.join(batch_dir, f))
print(" Папка очищена")

print("\n  ВАЖНО: Открой ОТДЕЛЬНОЕ окно и выполни: nvidia-smi -l 1")
input("Нажми Enter чтобы начать тест (5 генераций)...")

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
            seed=1000 + i,
            name="portrait"
        )
        elapsed = time.time() - start
        success += 1
        print(f" Итого: {elapsed:.1f} сек")
    except Exception as e:
        print(f" ПАДЕНИЕ на генерации #{i+1}: {e}")
        break

print("\n" + "="*60)
print(f"  Результат: {success}/5")
print("="*60)
