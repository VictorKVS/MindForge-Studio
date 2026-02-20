"""
Smoke Test  тест стабильности генерации.
Генерирует 10 изображений стандартного качества.
"""
import sys
sys.path.insert(0, '.')

from core.adapters.comfyui import ComfyUIAdapter
import time
import os
from pathlib import Path

def main():
    print("=" * 60)
    print(" SMOKE TEST: 10 генераций подряд")
    print("=" * 60)
    
    # Инициализация адаптера
    adapter = ComfyUIAdapter()
    
    # Проверка сервера
    print("\n Проверка сервера ComfyUI...", end=" ")
    if not adapter.health_check():
        print(" Недоступен")
        print("   Запустите: cd G:\\1\\AI\\ComfyUI && .\\run_nvidia_gpu.bat --listen 0.0.0.0")
        return 1
    print(" Доступен")
    
    # Создание папки для результатов
    output_dir = Path("sd/outputs/test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Очистка папки
    print(f"\n Очистка папки: {output_dir}")
    for f in output_dir.glob("*.png"):
        f.unlink()
    
    # Промпты для теста
    prompt = "professional business portrait of a confident woman in elegant suit, studio lighting, sharp focus, natural expression, perfect facial proportions, symmetrical face, professional corporate style"
    
    negative = "ugly, blurry, deformed face, bad anatomy, extra limbs, distorted features, asymmetrical face, bad proportions, cartoon, anime, poorly drawn face, mutation, mutated, disfigured"
    
    # Запуск генерации
    print("\n" + "=" * 60)
    print(" ЗАПУСК ГЕНЕРАЦИИ")
    print("=" * 60)
    
    start_time = time.time()
    result = adapter.generate_batch(
        prompt=prompt,
        negative=negative,
        quality="standard",
        count=10,
        seed_base=1000
    )
    total_time = time.time() - start_time
    
    # Перемещение файлов в папку результатов
    print("\n" + "=" * 60)
    print(" ПЕРЕМЕЩЕНИЕ ФАЙЛОВ")
    print("=" * 60)
    
    batch_dir = Path(r"G:\1\AI\ComfyUI\ComfyUI\output\batch")
    moved_count = 0
    
    for i, img_result in enumerate(result["images"]):
        if img_result["success"]:
            src_path = Path(img_result["image_path"])
            dst_path = output_dir / f"test_{i+1:02d}.png"
            
            try:
                src_path.rename(dst_path)
                moved_count += 1
                print(f" {dst_path.name}")
            except Exception as e:
                print(f" Ошибка перемещения: {e}")
    
    # Итоговый отчёт
    print("\n" + "=" * 60)
    print(" ИТОГОВЫЙ ОТЧЁТ")
    print("=" * 60)
    print(f"Запрошено: {result['total_requested']}")
    print(f"Успешно: {result['success_count']}")
    print(f"Ошибок: {result['failed_count']}")
    print(f"Перемещено: {moved_count}")
    print(f"Общее время: {total_time:.2f} сек")
    print(f"Среднее время на изображение: {total_time / result['success_count']:.2f} сек" if result['success_count'] > 0 else "Нет успешных генераций")
    print(f"Результаты: {output_dir}")
    
    # Проверка стабильности
    print("\n" + "=" * 60)
    if result["success_count"] == 10:
        print("  ТЕСТ ПРОЙДЕН: 10/10 генераций успешны")
        print(" Система стабильна для массовой генерации")
    else:
        print("   ТЕСТ НЕ ПРОЙДЕН")
        print(f" Успешно только {result['success_count']}/10")
    print("=" * 60)
    
    return 0 if result["success_count"] == 10 else 1

if __name__ == "__main__":
    sys.exit(main())
