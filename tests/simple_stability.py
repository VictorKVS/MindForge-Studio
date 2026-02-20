import sys
sys.path.insert(0, '.')

from core.adapters.comfyui import ComfyUIAdapter
import time

print(" ТЕСТ СТАБИЛЬНОСТИ (минимальная рабочая версия)")
print("="*60)

adapter = ComfyUIAdapter()
if not adapter.health_check():
    print(" ComfyUI не запущен")
    sys.exit(1)

print(" ComfyUI запущен")
print("\nГенерация 10 изображений...")

for i in range(10):
    try:
        start = time.time()
        result = adapter.generate(
            prompt="professional portrait woman",
            negative_prompt="ugly, blurry",
            width=512,
            height=640,
            seed=42 + i
        )
        elapsed = time.time() - start
        print(f" #{i+1} | {elapsed:.1f} сек | {result['image_path']}")
    except Exception as e:
        print(f" #{i+1} | Ошибка: {e}")
        break

print("="*60)
