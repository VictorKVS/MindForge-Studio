import sys
sys.path.insert(0, '.')

from core.adapters.comfyui import ComfyUIAdapter
import time

print("="*60)
print(" ТЕСТ С ЛОГИРОВАНИЕМ")
print(" Запись метрик в: logs/generation_log_*.log")
print("="*60)

adapter = ComfyUIAdapter()
if not adapter.health_check():
    print(" ComfyUI не запущен")
    sys.exit(1)

print(" ComfyUI запущен")
print("\nГенерация 5 изображений (остановимся при первом падении)...\n")

for i in range(5):
    print(f"\n{'='*60}")
    print(f"  Попытка #{i+1}/5")
    print(f"{'='*60}")
    
    try:
        result = adapter.generate(
            prompt="professional portrait woman",
            negative_prompt="ugly, blurry",
            width=512,
            height=512,
            seed=42 + i
        )
        print(f" Успех: {result['image_path']}")
    except Exception as e:
        print(f" Падение на попытке #{i+1}: {e}")
        break

print("\n" + "="*60)
print(" Тест завершён. Логи сохранены в папку 'logs'")
print("="*60)
