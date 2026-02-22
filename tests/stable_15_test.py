import sys
sys.path.insert(0, '.')
from core.adapters.comfyui import ComfyUIAdapter
import time, os

print("="*60)
print(" ТЕСТ: 15 ГЕНЕРАЦИЙ С ИДЕАЛЬНЫМИ ЛИЦАМИ")
print(" 320x320, 8 шагов, пауза 2 сек")
print("="*60)

adapter = ComfyUIAdapter()
if not adapter.health_check():
    print(" ComfyUI не запущен")
    sys.exit(1)
print(" ComfyUI запущен")

batch_dir = r"G:\1\AI\ComfyUI\ComfyUI\output\batch"
for f in os.listdir(batch_dir):
    if f.endswith('.png'):
        os.remove(os.path.join(batch_dir, f))
print(" Папка очищена")

prompts = [
    ("business_woman", "professional business portrait of a confident woman in elegant suit, studio lighting, sharp focus, natural expression, perfect facial proportions, symmetrical face", "ugly, blurry, deformed face, bad anatomy, distorted features, asymmetrical face, bad proportions"),
    ("business_man", "professional business portrait of a confident man in tailored suit, studio lighting, sharp focus, natural expression, perfect facial proportions, symmetrical face", "ugly, blurry, deformed face, bad anatomy, distorted features, asymmetrical face, bad proportions"),
    ("medical_doctor", "professional female doctor in white coat, stethoscope, confident medical portrait, clean background, clinical lighting, perfect facial proportions, symmetrical face", "ugly, blurry, deformed face, blood, gore, bad anatomy, distorted features"),
    ("medical_nurse", "friendly female nurse smiling, professional healthcare portrait, white uniform, caring expression, perfect facial proportions, symmetrical face", "ugly, blurry, deformed face, blood, gore, bad anatomy, distorted features"),
    ("creative_artistic", "artistic portrait, dramatic lighting, creative composition, fine art photography, perfect facial proportions, symmetrical face", "ugly, blurry, deformed face, bad anatomy, distorted features, amateur")
]

success = 0
for i in range(15):
    print(f"\n{'='*60}")
    print(f"  Генерация #{i+1}/15")
    print(f"{'='*60}")
    
    name, prompt, negative = prompts[i % len(prompts)]
    
    try:
        start = time.time()
        result = adapter.generate(
            prompt=prompt,
            negative=negative,
            width=320,
            height=320,
            seed=1000 + i
        )
        elapsed = time.time() - start
        success += 1
        print(f" {name} | {elapsed:.1f} сек | {os.path.basename(result['image_path'])}")
    except Exception as e:
        print(f" Падение на генерации #{i+1}: {e}")
        break

print("\n" + "="*60)
print(f" Успешно: {success}/15")
print("="*60)
