import sys
sys.path.insert(0, '.')
from core.adapters.comfyui import ComfyUIAdapter
import time, json, os
from pathlib import Path

def generate_batch(output_dir="batch_output", count=50):
    Path(output_dir).mkdir(exist_ok=True)
    adapter = ComfyUIAdapter()
    
    print("="*60)
    print(f"  ГЕНЕРАЦИЯ {count} ИЗОБРАЖЕНИЙ ДЛЯ ПРОДАЖИ")
    print("="*60)
    
    # УЛУЧШЕННЫЕ ПРОМПТЫ для идеальных пропорций лиц
    templates = [
        # Бизнес-портреты женщины (15 изображений)
        ("business_woman", 15, {
            "prompt": "professional business portrait of a confident woman in elegant suit, studio lighting, sharp focus, natural expression, perfect facial proportions, symmetrical face, professional corporate style, high detail photography",
            "negative": "ugly, blurry, deformed face, bad anatomy, extra limbs, distorted features, asymmetrical face, bad proportions, cartoon, anime, poorly drawn face, mutation, mutated, disfigured, poorly drawn hands, missing limbs, malformed hands, long neck"
        }),
        # Бизнес-портреты мужчины (15 изображений)
        ("business_man", 15, {
            "prompt": "professional business portrait of a confident man in tailored suit, studio lighting, sharp focus, natural expression, perfect facial proportions, symmetrical face, professional corporate style, high detail photography",
            "negative": "ugly, blurry, deformed face, bad anatomy, extra limbs, distorted features, asymmetrical face, bad proportions, cartoon, anime, poorly drawn face, mutation, mutated, disfigured, poorly drawn hands, missing limbs, malformed hands, long neck"
        }),
        # Медицинские портреты (10 изображений)
        ("medical_doctor", 10, {
            "prompt": "professional female doctor in white coat, stethoscope, confident medical portrait, clean background, clinical lighting, perfect facial proportions, symmetrical face, high detail photography",
            "negative": "ugly, blurry, deformed face, blood, gore, cartoon, unprofessional, bad anatomy, distorted features, asymmetrical face, bad proportions, poorly drawn face, mutation, mutated"
        }),
        # Креативные портреты (10 изображений)
        ("creative_artistic", 10, {
            "prompt": "artistic portrait, dramatic lighting, creative composition, fine art photography, perfect facial proportions, symmetrical face, unique expression, high detail",
            "negative": "ugly, blurry, deformed face, bad anatomy, distorted features, asymmetrical face, bad proportions, cartoon, amateur, poorly drawn face, mutation, mutated"
        })
    ]
    
    generated = []
    total_generated = 0
    
    for name, target_count, template in templates:
        if total_generated >= count:
            break
            
        print(f"\n Генерация: {name} ({target_count} изображений)")
        
        for i in range(target_count):
            if total_generated >= count:
                break
                
            try:
                print(f"  [{total_generated+1}/{count}] {name} #{i+1}...", end=" ")
                
                start_time = time.time()
                result = adapter.generate(
                    prompt=template["prompt"],
                    negative=template["negative"],
                    width=320,
                    height=320,
                    seed=1000 + total_generated
                )
                elapsed = time.time() - start_time
                
                metadata = {
                    "template": name,
                    "category": name.split('_')[0],
                    "generation_time_sec": elapsed,
                    "width": 320,
                    "height": 320,
                    "model": "v1-5-pruned-emaonly.safetensors",
                    "filename": f"{name}_{i+1:03d}.png"
                }
                
                generated.append({
                    "path": result["image_path"],
                    "metadata": metadata,
                    "success": True
                })
                
                print(f" {elapsed:.2f} сек")
                total_generated += 1
                
                # Пауза для стабильности
                time.sleep(0.5)
                
            except Exception as e:
                print(f" Ошибка: {e}")
                generated.append({
                    "path": None,
                    "metadata": {"template": name, "error": str(e)},
                    "success": False
                })
    
    # Сохраняем отчёт
    report = {
        "total_target": count,
        "total_generated": total_generated,
        "success_count": sum(1 for g in generated if g["success"]),
        "failed_count": sum(1 for g in generated if not g["success"]),
        "images": generated,
        "timestamp": time.time()
    }
    
    report_path = Path(output_dir) / "generation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*60)
    print("  ГЕНЕРАЦИЯ ЗАВЕРШЕНА")
    print("="*60)
    print(f"  Всего сгенерировано: {total_generated}/{count}")
    print(f"  Успешно: {report['success_count']}")
    print(f"  Ошибок: {report['failed_count']}")
    print(f"  Отчёт: {report_path}")
    print("="*60)
    
    return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Генерация пакета изображений для продажи")
    parser.add_argument("--count", type=int, default=50, help="Количество изображений")
    parser.add_argument("--output", type=str, default="batch_output", help="Папка для сохранения")
    args = parser.parse_args()
    
    generate_batch(output_dir=args.output, count=args.count)
