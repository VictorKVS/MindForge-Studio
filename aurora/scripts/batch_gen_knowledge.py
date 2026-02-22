# ========================================
# Название: Batch Generator с Art Director
# Описание: Автоматическая сборка промптов + генерация
# Версия: 4.0.0 (Knowledge Base Integration)
# ========================================

import sys
import os
import time
import shutil
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.adapters.comfyui import ComfyUIAdapter
from aurora.services.quality_checker import QualityChecker
from core.agents.art_director import ArtDirectorAgent

BASE_NEGATIVE = (
    "ugly, blurry, deformed face, bad anatomy, extra limbs, distorted features, "
    "asymmetrical face, bad proportions, cartoon, anime, poorly drawn face, "
    "mutation, mutated, disfigured, poorly drawn hands, missing limbs, "
    "malformed hands, long neck, text, watermark, signature, low quality, jpeg artifacts"
)

CONFIG = {
    "total_images": 50,
    "seed_base": 6000,
    "cool_down_every": 10,
    "cool_down_seconds": 30,
    "output_folder": "aurora/output/batch_knowledge",
    "rejected_folder": "aurora/output/rejected_knowledge",
    "min_quality_score": 0.7,
    "max_retries": 2,
}

# Заказы для генерации (можно расширять)
ORDERS = [
    {
        "style": "business",
        "emotion": "confidence",
        "pose": "three_quarter",
        "lighting": "studio",
        "subject": "professional woman in elegant suit"
    },
    {
        "style": "cinematic",
        "emotion": "mysterious",
        "pose": "profile",
        "lighting": "dramatic",
        "subject": "woman in dark atmosphere"
    },
    {
        "style": "fashion",
        "emotion": "seductive",
        "pose": "over_shoulder",
        "lighting": "rim",
        "subject": "model in designer clothing"
    },
]

def clean_output_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f" Очистка папки: {folder_path}")
    os.makedirs(folder_path, exist_ok=True)
    print(f" Папка создана: {folder_path}")

def copy_image_to_output(comfyui_path, output_folder, img_id, seed):
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
    print("=" * 80)
    print(" AURORA BATCH GENERATOR + ART DIRECTOR (Knowledge Base)")
    print("=" * 80)
    
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
    art_director = ArtDirectorAgent()
    
    print(f" План: {CONFIG['total_images']} изображений")
    print(f" Заказов в ротации: {len(ORDERS)}")
    print(f" Мин. score: {CONFIG['min_quality_score']}")
    print("=" * 80)
    
    success_count = 0
    rejected_count = 0
    
    for i in range(CONFIG["total_images"]):
        img_id = i + 1
        seed = CONFIG["seed_base"] + i
        
        # Циклический выбор заказа
        order = ORDERS[i % len(ORDERS)]
        
        # Art Director собирает промпт
        prompt_config = art_director.assemble_prompt(order)
        
        retries_left = CONFIG["max_retries"]
        saved = False
        
        print(f"\n[{img_id}/{CONFIG['total_images']}] {order['style']} (seed={seed})...", end=" ")
        
        while retries_left >= 0 and not saved:
            try:
                result = adapter.generate(
                    prompt=prompt_config["prompt"],
                    negative=prompt_config["negative"] + ", " + BASE_NEGATIVE,
                    quality="high",
                    seed=seed,
                    custom_params={
                        "width": int(prompt_config["resolution"].split("x")[0]),
                        "height": int(prompt_config["resolution"].split("x")[1]),
                        "steps": prompt_config["steps"],
                        "cfg": prompt_config["cfg"]
                    }
                )
                
                if result and 'image_path' in result:
                    comfyui_path = result['image_path']
                    project_path = copy_image_to_output(
                        comfyui_path, CONFIG["output_folder"], img_id, seed
                    )
                    
                    if project_path:
                        quality_result = checker.evaluate(project_path)
                        
                        if quality_result["passed"]:
                            print(f" (score={quality_result['score']})")
                            checker.save_report(project_path, quality_result)
                            success_count += 1
                            saved = True
                        else:
                            move_to_rejected(project_path, CONFIG["rejected_folder"], img_id, seed)
                            print(f" (score={quality_result['score']})")
                            rejected_count += 1
                            
                            if retries_left > 0:
                                retries_left -= 1
                            else:
                                print(f"     Лимит исчерпан")
                    else:
                        retries_left -= 1
                else:
                    retries_left -= 1
                    
            except Exception as e:
                print(f" Ошибка: {e}")
                retries_left -= 1
                time.sleep(5)
        
        if img_id % CONFIG["cool_down_every"] == 0:
            print(f" Охлаждение ({CONFIG['cool_down_seconds']} сек)...")
            time.sleep(CONFIG["cool_down_seconds"])
    
    print("=" * 80)
    print(f" ЗАВЕРШЕНО")
    print(f"    Успешно: {success_count}/{CONFIG['total_images']}")
    print(f"    Отбраковано: {rejected_count}")
    print(f"    Процент качества: {success_count/CONFIG['total_images']*100:.1f}%")
    print("=" * 80)

if __name__ == "__main__":
    run_batch()
