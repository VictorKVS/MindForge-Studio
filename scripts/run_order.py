"""
Запуск заказа по YAML-файлу.
"""
import sys
import yaml
from pathlib import Path
sys.path.insert(0, '.')

from core.adapters.comfyui import ComfyUIAdapter
from core.schemas.order import Order
import json
import time

def load_order(file_path: str) -> Order:
    """Загрузка заказа из YAML файла."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Валидация через pydantic
    order = Order(**data)
    print(f" Заказ загружен: {order.order_id}")
    print(f"   Тип: {order.type}")
    print(f"   Количество: {order.count}")
    print(f"   Качество: {order.quality.value}")
    return order

def run_order(order: Order) -> dict:
    """Выполнение заказа."""
    print("\n" + "="*60)
    print(f" ЗАПУСК ЗАКАЗА: {order.order_id}")
    print("="*60)
    
    # Инициализация адаптера
    adapter = ComfyUIAdapter()
    
    # Проверка сервера
    if not adapter.health_check():
        raise Exception("ComfyUI сервер недоступен")
    
    # Формирование промпта на основе заказа
    prompt_parts = [
        f"professional {order.style.preset} portrait",
        f"of a {order.subject.gender}",
        f"age {order.subject.age_range}",
    ]
    
    if order.style.clothing:
        prompt_parts.append(f"wearing {order.style.clothing}")
    
    if order.style.background:
        prompt_parts.append(f"on {order.style.background} background")
    
    prompt_parts.extend([
        "studio lighting",
        "sharp focus",
        "natural expression",
        "perfect facial proportions",
        "symmetrical face",
        "high detail photography"
    ])
    
    prompt = ", ".join(prompt_parts)
    
    # Формирование негатива
    negative = "ugly, blurry, deformed face, bad anatomy, extra limbs, distorted features, asymmetrical face, bad proportions, cartoon, anime, poorly drawn face, mutation, mutated, disfigured"
    
    # Генерация
    print(f"\n Генерация {order.count} изображений...")
    print(f"   Промпт: {prompt}")
    
    start_time = time.time()
    result = adapter.generate_batch(
        prompt=prompt,
        negative=negative,
        quality=order.quality.value,
        count=order.count,
        seed_base=order.seed_base
    )
    total_time = time.time() - start_time
    
    # Создание отчёта
    report = {
        "order_id": order.order_id,
        "status": "completed" if result["success_count"] == order.count else "partial",
        "total_requested": order.count,
        "total_generated": result["total_generated"],
        "success_count": result["success_count"],
        "failed_count": result["failed_count"],
        "total_time_sec": total_time,
        "average_time_sec": total_time / result["success_count"] if result["success_count"] > 0 else 0,
        "images": result["images"],
        "parameters": {
            "quality": order.quality.value,
            "count": order.count,
            "seed_base": order.seed_base
        }
    }
    
    # Сохранение отчёта
    output_dir = Path(order.output.target_folder) if order.output.target_folder else Path(f"sd/outputs/{order.order_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = output_dir / "generation_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n Отчёт сохранён: {report_path}")
    
    return report

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Запуск заказа по YAML-файлу")
    parser.add_argument("--file", "-f", required=True, help="Путь к файлу заказа YAML")
    args = parser.parse_args()
    
    try:
        order = load_order(args.file)
        report = run_order(order)
        
        print("\n" + "="*60)
        print(" ИТОГОВЫЙ ОТЧЁТ")
        print("="*60)
        print(f"Заказ: {report['order_id']}")
        print(f"Статус: {report['status']}")
        print(f"Успешно: {report['success_count']}/{report['total_requested']}")
        print(f"Ошибок: {report['failed_count']}")
        print(f"Общее время: {report['total_time_sec']:.2f} сек")
        print(f"Среднее время: {report['average_time_sec']:.2f} сек/изображение")
        
        return 0 if report["status"] == "completed" else 1
        
    except Exception as e:
        print(f"\n Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
