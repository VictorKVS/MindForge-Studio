import sys
from pathlib import Path

# Добавляем корень проекта в sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.adapters.comfyui import ComfyUIAdapter
import time

print("="*60)
print(" Тест стабильности: 10 генераций с очисткой VRAM")
print("="*60)

adapter = ComfyUIAdapter()

for i in range(10):
    print(f"\n Генерация #{i+1}/10")
    print("-" * 60)
    
    try:
        start_time = time.time()
        result = adapter.generate(
            prompt="professional portrait photo of a woman, sharp eyes, natural skin texture",
            negative_prompt="ugly, blurry, deformed face",
            width=1024,
            height=1024
        )
        elapsed = time.time() - start_time
        
        print(f" Успех! Время: {elapsed:.2f} сек")
        print(f"   Путь: {result['image_path']}")
        
        # Пауза между генерациями
        time.sleep(1.0)
        
    except Exception as e:
        print(f" Ошибка на генерации #{i+1}: {e}")
        import traceback
        traceback.print_exc()
        break

print("\n" + "="*60)
print(" Тест завершён!")
print("="*60)
