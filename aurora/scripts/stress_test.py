# ========================================
# Название скрипта: AURORA Stress Test
# Описание: Тест максимальных нагрузок
# Автор: AURORA Team
# Дата: 2026-02-19
# Версия: 1.0.0
# ========================================

import sys
import os
import time
import shutil
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.adapters.comfyui import ComfyUIAdapter
from aurora.services.quality_checker import QualityChecker

# ========================================
# КОНФИГУРАЦИЯ СТРЕСС-ТЕСТА
# ========================================

STRESS_CONFIG = {
    "total_images": 100,
    "seed_base": 5000,
    "cool_down_every": 10,
    "cool_down_seconds": 45,
    "output_folder": "aurora/output/stress_test",
    "rejected_folder": "aurora/output/stress_rejected",
    "min_quality_score": 0.7,
    "max_retries": 3,
    "test_resolutions": [
        {"width": 512, "height": 512, "label": "512x512"},
        {"width": 768, "height": 768, "label": "768x768"},
        {"width": 1024, "height": 1024, "label": "1024x1024"}
    ],
    "custom_params_base": {
        "steps": 30,
        "cfg": 6.0
    }
}

BASE_FACE_RULES = (
    "perfect facial proportions, symmetrical face, sharp focus, natural expression, "
    "highly detailed, photorealistic, 8k, masterpieces"
)

BASE_NEGATIVE = (
    "ugly, blurry, deformed face, bad anatomy, extra limbs, distorted features, "
    "asymmetrical face, bad proportions, cartoon, anime, poorly drawn face, "
    "mutation, mutated, disfigured, poorly drawn hands, missing limbs, "
    "malformed hands, long neck, text, watermark, signature, low quality, jpeg artifacts"
)

PROMPT_BASE = "professional portrait of a woman, studio lighting, elegant suit"

# ========================================
# ФУНКЦИИ
# ========================================

def clean_output_folder(folder_path):
    """Очистка папки перед тестом"""
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f" Очистка папки: {folder_path}")
    os.makedirs(folder_path, exist_ok=True)
    print(f" Папка создана: {folder_path}")

def copy_image_to_output(comfyui_path, output_folder, img_id, seed, resolution):
    """Копирование изображения с уникальным именем"""
    os.makedirs(output_folder, exist_ok=True)
    
    timestamp = datetime.now().strftime("%H%M%S%f")
    dest_name = f"stress_{resolution}_{img_id:03d}_seed{seed}_{timestamp}.png"
    dest_path = os.path.join(output_folder, dest_name)
    
    try:
        shutil.copy2(comfyui_path, dest_path)
        return dest_path
    except Exception as e:
        print(f" Ошибка копирования: {e}")
        return None

def move_to_rejected(source_path, rejected_folder, img_id, seed):
    """Перемещение бракованного изображения"""
    os.makedirs(rejected_folder, exist_ok=True)
    
    timestamp = datetime.now().strftime("%H%M%S%f")
    dest_name = f"rejected_{img_id:03d}_seed{seed}_{timestamp}.png"
    dest_path = os.path.join(rejected_folder, dest_name)
    
    try:
        shutil.move(source_path, dest_path)
        return dest_path
    except Exception as e:
        print(f" Ошибка перемещения: {e}")
        return None

def run_stress_test():
    print("=" * 80)
    print(" AURORA STRESS TEST  МАКСИМАЛЬНЫЕ НАГРУЗКИ")
    print("=" * 80)
    print(f" Всего изображений: {STRESS_CONFIG['total_images']}")
    print(f" Тест разрешений: {[r['label'] for r in STRESS_CONFIG['test_resolutions']]}")
    print(f" CFG: {STRESS_CONFIG['custom_params_base']['cfg']}")
    print(f" Шаги: {STRESS_CONFIG['custom_params_base']['steps']}")
    print(f" Мин. score: {STRESS_CONFIG['min_quality_score']}")
    print(f" Макс. попыток: {STRESS_CONFIG['max_retries']}")
    print("=" * 80)
    
    clean_output_folder(STRESS_CONFIG["output_folder"])
    os.makedirs(STRESS_CONFIG["rejected_folder"], exist_ok=True)
    
    adapter = ComfyUIAdapter()
    checker = QualityChecker({
        "min_quality_score": STRESS_CONFIG["min_quality_score"],
        "min_resolution": 512,
        "min_sharpness": 0.3,
        "min_brightness": 0.2,
        "max_brightness": 0.8
    })
    
    full_prompt = f"{PROMPT_BASE}, {BASE_FACE_RULES}"
    full_negative = BASE_NEGATIVE
    
    # Статистика
    stats = {
        "total": 0,
        "success": 0,
        "rejected": 0,
        "retries": 0,
        "errors": 0,
        "by_resolution": {}
    }
    
    start_time = time.time()
    
    for i in range(STRESS_CONFIG["total_images"]):
        img_id = i + 1
        seed = STRESS_CONFIG["seed_base"] + i
        
        # Циклический выбор разрешения
        res_index = i % len(STRESS_CONFIG["test_resolutions"])
        resolution = STRESS_CONFIG["test_resolutions"][res_index]
        res_label = resolution["label"]
        
        if res_label not in stats["by_resolution"]:
            stats["by_resolution"][res_label] = {"success": 0, "rejected": 0}
        
        retries_left = STRESS_CONFIG["max_retries"]
        saved = False
        
        print(f"\n[{img_id}/{STRESS_CONFIG['total_images']}] {res_label} (seed={seed})...", end=" ")
        
        while retries_left >= 0 and not saved:
            try:
                custom_params = {
                    "width": resolution["width"],
                    "height": resolution["height"],
                    "steps": STRESS_CONFIG["custom_params_base"]["steps"],
                    "cfg": STRESS_CONFIG["custom_params_base"]["cfg"]
                }
                
                result = adapter.generate(
                    prompt=full_prompt,
                    negative=full_negative,
                    quality="high",
                    seed=seed + stats["retries"],
                    custom_params=custom_params
                )
                
                if result and 'image_path' in result:
                    comfyui_path = result['image_path']
                    
                    project_path = copy_image_to_output(
                        comfyui_path,
                        STRESS_CONFIG["output_folder"],
                        img_id,
                        seed,
                        res_label
                    )
                    
                    if project_path:
                        quality_result = checker.evaluate(project_path)
                        
                        if quality_result["passed"]:
                            print(f" Успешно (score={quality_result['score']})")
                            checker.save_report(project_path, quality_result)
                            stats["success"] += 1
                            stats["by_resolution"][res_label]["success"] += 1
                            saved = True
                        else:
                            move_to_rejected(
                                project_path,
                                STRESS_CONFIG["rejected_folder"],
                                img_id,
                                seed
                            )
                            print(f" Отбраковано (score={quality_result['score']})")
                            stats["rejected"] += 1
                            stats["by_resolution"][res_label]["rejected"] += 1
                            
                            if retries_left > 0:
                                print(f"    Повтор... ({retries_left} попыток)")
                                retries_left -= 1
                                stats["retries"] += 1
                            else:
                                print(f"     Лимит исчерпан")
                    else:
                        print(" Ошибка копирования")
                        retries_left -= 1
                else:
                    print(" Ошибка (пустой результат)")
                    retries_left -= 1
                    
            except Exception as e:
                print(f" Ошибка: {e}")
                stats["errors"] += 1
                retries_left -= 1
                time.sleep(5)
        
        stats["total"] += 1
        
        # Охлаждение
        if img_id % STRESS_CONFIG["cool_down_every"] == 0:
            elapsed = time.time() - start_time
            print(f" Охлаждение ({STRESS_CONFIG['cool_down_seconds']} сек)... Прошло: {elapsed:.0f} сек")
            time.sleep(STRESS_CONFIG["cool_down_seconds"])
    
    # Итоговый отчёт
    total_time = time.time() - start_time
    
    print("=" * 80)
    print(" СТРЕСС-ТЕСТ ЗАВЕРШЁН")
    print("=" * 80)
    print(f" Общее время: {total_time:.0f} сек ({total_time/60:.1f} мин)")
    print(f" Всего: {stats['total']}")
    print(f" Успешно: {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
    print(f" Отбраковано: {stats['rejected']}")
    print(f" Повторов: {stats['retries']}")
    print(f"  Ошибок: {stats['errors']}")
    print("=" * 80)
    print(" ПО РАЗРЕШЕНИЯМ:")
    for res, data in stats["by_resolution"].items():
        total_res = data["success"] + data["rejected"]
        if total_res > 0:
            percent = data["success"] / total_res * 100
            print(f"   {res}:  {data['success']} /  {data['rejected']} ({percent:.1f}%)")
    print("=" * 80)
    
    # Сохранение отчёта
    report = {
        "test_id": f"stress_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "total_images": stats["total"],
        "success": stats["success"],
        "rejected": stats["rejected"],
        "retries": stats["retries"],
        "errors": stats["errors"],
        "total_time_sec": round(total_time, 2),
        "by_resolution": stats["by_resolution"],
        "config": STRESS_CONFIG
    }
    
    report_path = os.path.join(STRESS_CONFIG["output_folder"], "stress_report.json")
    import json
    with open(report_path, 'w', encoding='utf8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f" Отчёт сохранён: {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    run_stress_test()
