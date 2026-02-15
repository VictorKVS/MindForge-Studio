import requests, json, time, os, sys
from pathlib import Path

print("="*60)
print(" SDXL генерация через ComfyUI")
print("="*60)

# Проверка сервера
try:
    requests.get("http://127.0.0.1:8188", timeout=5)
    print(" ComfyUI доступен")
except:
    print(" Ошибка: ComfyUI не отвечает")
    print("   Запусти в отдельном окне: cd G:\\1\\AI\\ComfyUI && .\\run_nvidia_gpu.bat")
    sys.exit(1)

# Пайплайн SDXL
payload = {
    "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
    "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "professional portrait photo of a woman, sharp eyes, natural skin texture", "clip": ["1", 1]}},
    "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "professional portrait photo of a woman, sharp eyes, natural skin texture", "clip": ["1", 0]}},
    "4": {"class_type": "CLIPTextEncode", "inputs": {"text": "ugly, blurry, deformed face", "clip": ["1", 1]}},
    "5": {"class_type": "CLIPTextEncode", "inputs": {"text": "ugly, blurry, deformed face", "clip": ["1", 0]}},
    "6": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
    "7": {"class_type": "KSampler", "inputs": {
        "model": ["1", 0], "positive": ["2", 0], "negative": ["4", 0],
        "latent_image": ["6", 0], "seed": 42, "steps": 25, "cfg": 7.0,
        "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0
    }},
    "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
    "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "test_run/sdxl_portrait"}}
}

print(" Отправка SDXL запроса (1024x1024)...")
resp = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": payload}, timeout=10)
resp.raise_for_status()
print(" Запрос принят. Генерация ~30 сек (SDXL тяжелее)...")

# Ожидание файла
out_dir = Path(r"G:\1\AI\ComfyUI\output\test_run")
start = time.time()
while time.time() - start < 60:
    if out_dir.exists() and any(f.endswith('.png') for f in os.listdir(out_dir)):
        pngs = sorted([f for f in os.listdir(out_dir) if f.endswith('.png')], reverse=True)
        print(f"\n УСПЕХ! SDXL изображение:\n   {out_dir / pngs[0]}")
        print("="*60)
        sys.exit(0)
    time.sleep(2)
    print(".", end="", flush=True)

print("\n\n Таймаут  проверь лог сервера (не хватает VRAM?)")
sys.exit(1)
