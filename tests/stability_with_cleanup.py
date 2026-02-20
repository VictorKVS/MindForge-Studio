import sys
sys.path.insert(0, '.')

from core.adapters.comfyui import ComfyUIAdapter
import time

print("="*60)
print(" ТЕСТ СТАБИЛЬНОСТИ С ОЧИСТКОЙ ПАМЯТИ")
print(" 10 генераций подряд (как раньше)")
print("="*60)

adapter = ComfyUIAdapter()

if not adapter.health_check():
    print(" ComfyUI не запущен!")
    sys.exit(1)

print(" ComfyUI запущен\n")

success = 0
for i in range(10):
    print(f" #{i+1}/10", end=" ")
    
    try:
        start = time.time()
        result = adapter.generate(
            prompt="professional portrait photo of a woman",
            negative_prompt="ugly, blurry",
            width=512,
            height=640,
            seed=42 + i,
            category="business"
        )
        elapsed = time.time() - start
        
        print(f" {elapsed:.1f} сек | {result['folder_name']}")
        success += 1
        
    except Exception as e:
        print(f" {e}")
        break

print("\n" + "="*60)
print(f" Успешно: {success}/10")
print("="*60)

if success == 10:
    print(" СТАБИЛЬНОСТЬ ДОСТИГНУТА! 10/10 без падений.")
    print("   Готов к массовой генерации для продажи.")
