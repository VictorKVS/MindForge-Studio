import sys
sys.path.insert(0, '.')
from core.adapters.comfyui import ComfyUIAdapter
import time

print("="*60)
print(" ТЕСТ БЕЗОПАСНОГО РЕЖИМА")
print(" Настройки: 448x448, 12 шагов, пауза 3 сек")
print("="*60)

adapter = ComfyUIAdapter()
if not adapter.health_check():
    print(" ComfyUI не запущен")
    sys.exit(1)
print(" ComfyUI запущен")

print("\nГенерация 10 изображений с паузой 3 сек между ними...\n")
for i in range(10):
    print(f" Генерация #{i+1}/10...", end=" ")
    sys.stdout.flush()
    
    try:
        start = time.time()
        result = adapter.generate(
            prompt="professional portrait woman",
            negative="ugly, blurry",
            width=448,
            height=448,
            seed=42 + i
        )
        elapsed = time.time() - start
        print(f" {elapsed:.1f} сек | {result['image_path']}")
    except Exception as e:
        print(f" Ошибка: {e}")
        break

print("\n" + "="*60)
print(" Тест завершён")
print("="*60)
