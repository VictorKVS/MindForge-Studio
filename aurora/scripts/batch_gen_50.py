# ========================================
# Название: AURORA Batch Generator 50
# Описание: Пакетная генерация с Quality Control
# Версия: 3.3.0 (Исправлены конфликты имён)
# ========================================

import sys
import os
import time
import shutil
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.adapters.comfyui import ComfyUIAdapter
from aurora.services.quality_checker import QualityChecker

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

CONFIG = {
    "total_images": 50,
    "quality": "high",
    "seed_base": 3000,
    "cool_down_every": 10,
    "cool_down_seconds": 30,
    "comfyui_output": "G:\\1\\AI\\ComfyUI\\ComfyUI\\output",
    "output_folder": "aurora/output/batch_50",
    "rejected_folder": "aurora/output/rejected",
    "min_quality_score": 0.7,
    "max_retries": 2,
    "custom_params": {
        "width": 512,
        "height": 512,
        "steps": 25,
        "cfg": 5.5
    }
}

PROMPT_BASE = "professional portrait of a woman, studio lighting, elegant suit"

def clean_output_folder(folder_path):
    """Очистка папки перед генерацией"""
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f" Очистка папки: {folder_path}")
    os.makedirs(folder_path, exist_ok=True)
    print(f" Папка создана: {folder_path}")

def copy_image_to_output(comfyui_path, output_folder, img_id, seed):
    """Копирование изображения из ComfyUI в папку проекта"""
    os.makedirs(output_folder, exist_ok=True)
    
    timestamp = datetime.now().strftime("%H%M%S%f")
    dest_name = f"image_{img_id:03d}_seed{seed}_{timestamp}.png"
    dest_path = os.path.join(output_folder, dest_name)
    
    try:
        shutil.copy2(comfyui_path, dest_path)
        return dest_path
    except Exception as e:
        print(f" Ошибка копирования: {e}")
        return None

def move_to_rejected(source_path, rejected_folder, img_id, seed):
    """Перемещение бракованного изображения с уникальным именем"""
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

def run_batch():
    print("=" * 60)
    print(" AURORA BATCH GENERATOR (LIVE MODE + QUALITY CHECK)")
    print("=" * 60)
    
    clean_output_folder(CONFIG["output_folder"])
    os.makedirs(CONFIG["rejected_folder"], exist_ok=True)
    
    adapter = ComfyUIAdapter()
    checker = QualityChecker({
        "min_quality_score": CONFIG["min_quality_score"],
        "min_resolution": 512,
        "min_sharpness": 0.3,
        "min_brightness": 0.2,
        "max_brightness": 0.8
    })
    
    full_prompt = f"{PROMPT_BASE}, {BASE_FACE_RULES}"
    full_negative = BASE_NEGATIVE
    
    print(f" План: {CONFIG['total_images']} изображений")
    print(f" Качество: {CONFIG['quality']}")
    print(f" Разрешение: {CONFIG['custom_params']['width']}x{CONFIG['custom_params']['height']}")
    print(f" CFG: {CONFIG['custom_params']['cfg']}")
    print(f" Мин. score: {CONFIG['min_quality_score']}")
    print("=" * 60)
    
    success_count = 0
    rejected_count = 0
    retry_count = 0
    
    for i in range(CONFIG["total_images"]):
        img_id = i + 1
        seed = CONFIG["seed_base"] + i
        retries_left = CONFIG["max_retries"]
        saved = False
        
        while retries_left >= 0 and not saved:
            print(f"\n[{img_id}/{CONFIG['total_images']}] Генерация (seed={seed})...", end=" ")
            
            try:
                result = adapter.generate(
                    prompt=full_prompt,
                    negative=full_negative,
                    quality=CONFIG["quality"],
                    seed=seed + retry_count,
                    custom_params=CONFIG["custom_params"]
                )
                
                if result and 'image_path' in result:
                    comfyui_path = result['image_path']
                    
                    project_path = copy_image_to_output(
                        comfyui_path,
                        CONFIG["output_folder"],
                        img_id,
                        seed
                    )
                    
                    if project_path:
                        quality_result = checker.evaluate(project_path)
                        
                        if quality_result["passed"]:
                            print(f" Успешно (score={quality_result['score']})")
                            checker.save_report(project_path, quality_result)
                            success_count += 1
                            saved = True
                        else:
                            move_to_rejected(
                                project_path,
                                CONFIG["rejected_folder"],
                                img_id,
                                seed
                            )
                            print(f" Отбраковано (score={quality_result['score']})")
                            rejected_count += 1
                            
                            if retries_left > 0:
                                print(f"    Повторная генерация... ({retries_left} попыток)")
                                retries_left -= 1
                                retry_count += 1
                            else:
                                print(f"     Лимит попыток исчерпан")
                    else:
                        print(" Ошибка копирования")
                        retries_left -= 1
                else:
                    print(" Ошибка (пустой результат)")
                    retries_left -= 1
                    
            except Exception as e:
                print(f" Ошибка: {e}")
                retries_left -= 1
                time.sleep(5)
        
        if img_id % CONFIG["cool_down_every"] == 0:
            print(f" Охлаждение ({CONFIG['cool_down_seconds']} сек)...")
            time.sleep(CONFIG["cool_down_seconds"])
    
    print("=" * 60)
    print(f" ЗАВЕРШЕНО")
    print(f"    Успешно: {success_count}/{CONFIG['total_images']}")
    print(f"    Отбраковано: {rejected_count}")
    print(f"    Повторов: {retry_count}")
    if CONFIG['total_images'] > 0:
        print(f"    Процент качества: {success_count/CONFIG['total_images']*100:.1f}%")
    print("=" * 60)

if __name__ == "__main__":
    run_batch()
