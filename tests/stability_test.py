import sys
sys.path.insert(0, '.')
from core.adapters.comfyui import ComfyUIAdapter
import time

print("="*60)
print(" ТЕСТ СТАБИЛЬНОСТИ С ЛОГИРОВАНИЕМ")
print(" Цель: найти предел до падения экрана")
print("="*60)

adapter = ComfyUIAdapter()
if not adapter.health_check():
    print(" ComfyUI не запущен")
    sys.exit(1)
print(" ComfyUI запущен")

print("\nГенерация до падения (макс. 10 изображений)...\n")
for i in range(10):
    print(f"\n{'='*60}")
    print(f"  Генерация #{i+1}/10")
    print(f"{'='*60}")
    try:
        start = time.time()
        result = adapter.generate(
            prompt="professional portrait woman",
            negative="ugly, blurry",
            width=512,
            height=512,
            seed=42 + i
        )
        elapsed = time.time() - start
        print(f" Успех за {elapsed:.1f} сек | {result['image_path']}")
    except Exception as e:
        print(f" ПАДЕНИЕ на генерации #{i+1}: {e}")
        print("\n  ЭКРАН ПОГАС! Запомни номер генерации.")
        break

print("\n" + "="*60)
print(" Тест завершён. Анализируй логи в папке 'logs'")
print("="*60)
