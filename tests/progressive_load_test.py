import sys
sys.path.insert(0, '.')
from core.adapters.comfyui import ComfyUIAdapter
import time
import os
import json

print("="*60)
print(" ТЕСТ: ПОСТЕПЕННОЕ УВЕЛИЧЕНИЕ НАГРУЗКИ")
print(" От 3 до 15 генераций на высоком разрешении")
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

# Тест на 3, 5, 10 и 15 генераций
test_sizes = [3, 5, 10, 15]
results = []

for size in test_sizes:
    print(f"\n{'='*60}")
    print(f" ТЕСТ: {size} генераций на разрешении 384x384")
    print(f"{'='*60}")
    
    success = 0
    for i in range(size):
        print(f"\nГенерация #{i+1}/{size}...", end=" ", flush=True)
        try:
            start = time.time()
            result = adapter.generate(
                prompt="professional portrait woman, perfect facial proportions, symmetrical face",
                negative="ugly, blurry, deformed face, bad anatomy, distorted features, asymmetrical face, bad proportions",
                quality="high",
                seed=3000 + i
            )
            elapsed = time.time() - start
            success += 1
            print(f" {elapsed:.1f} сек")
        except Exception as e:
            print(f" Ошибка: {e}")
            break
    
    results.append({
        "size": size,
        "success": success,
        "total": size,
        "success_rate": success / size
    })

# Сохраняем отчёт
report = {
    "test_name": "high_resolution_progressive_test",
    "timestamp": time.time(),
    "results": results
}

report_path = "tests\high_resolution_progressive_report.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print("\n" + "="*60)
print("  ТЕСТ ЗАВЕРШЁН")
print(f" Отчёт сохранён: {report_path}")
print("="*60)

# Выводим результат
print("\nРезультаты теста:")
for res in results:
    status = "" if res["success"] == res["total"] else ""
    print(f" {res['size']} генераций: {status} {res['success']}/{res['total']}")
