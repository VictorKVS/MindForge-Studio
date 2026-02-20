import sys
sys.path.insert(0, '.')

from core.adapters.comfyui import ComfyUIAdapter

print("="*60)
print(" Простой тест генерации (1 изображение)")
print("="*60)

adapter = ComfyUIAdapter()

if not adapter.health_check():
    print(" ComfyUI не запущен!")
    print("   Запусти: cd G:\\1\\AI\\ComfyUI && .\\run_nvidia_gpu.bat --listen 0.0.0.0")
    sys.exit(1)

print(" ComfyUI запущен")
print("\n Запускаем генерацию...")

try:
    result = adapter.generate(
        prompt="professional portrait photo of a woman",
        negative_prompt="ugly, blurry, deformed face",
        width=512,
        height=640
    )
    print(f"\n УСПЕХ!")
    print(f"   Путь: {result['image_path']}")
    print("="*60)
except Exception as e:
    print(f"\n ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
    print("="*60)
