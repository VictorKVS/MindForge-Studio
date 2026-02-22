import sys
sys.path.insert(0, '.')
from core.adapters.comfyui import ComfyUIAdapter
import time, os

print("="*60)
print(" ПРОСТОЙ ТЕСТ: 1 ГЕНЕРАЦИЯ")
print(" 320x320, 8 шагов")
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

print("\n Запуск генерации...")
print("="*60)

try:
    start = time.time()
    result = adapter.generate(
        prompt="simple portrait woman",
        negative="ugly, blurry",
        width=320,
        height=320,
        seed=42
    )
    elapsed = time.time() - start
    print("="*60)
    print(f" УСПЕХ! Время: {elapsed:.1f} сек")
    print(f" Файл: {result['image_path']}")
except Exception as e:
    print("="*60)
    print(f" ОШИБКА: {e}")
    print("\n Возможные причины:")
    print("1. ComfyUI не обрабатывает запрос (проверь логи сервера)")
    print("2. Модель не загружается (проверь имя файла)")
    print("3. Нет прав на запись в папку output")
