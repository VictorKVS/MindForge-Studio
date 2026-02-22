import sys
sys.path.insert(0, '.')
from core.adapters.comfyui import ComfyUIAdapter
import time

print("="*60)
print(" ТЕСТ ГЕНЕРАЦИИ С ЛОГИРОВАНИЕМ")
print(" Логи: logs/gen_*.log")
print("="*60)

adapter = ComfyUIAdapter()
if not adapter.health_check():
    print(" ComfyUI не запущен")
    sys.exit(1)
print(" ComfyUI запущен")

print("\nГенерация 5 изображений...\n")
for i in range(5):
    print(f"\n{'='*60}")
    print(f"  Попытка #{i+1}/5")
    print(f"{'='*60}")
    try:
        result = adapter.generate(
            prompt="professional portrait woman",
            negative="ugly, blurry",
            width=512,
            height=512,
            seed=42 + i
        )
        print(f" Успех: {result['image_path']}")
    except Exception as e:
        print(f" Падение на попытке #{i+1}: {e}")
        break

print("\n" + "="*60)
print(" Тест завершён. Логи в папке 'logs'")
print("="*60)
