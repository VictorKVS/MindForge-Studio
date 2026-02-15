import requests, time, os, sys
from pathlib import Path

print("="*60)
print(" ComfyUI Smoke Test (SD 1.5)  v0.13.0+ совместимый")
print("="*60)

try:
    requests.get("http://127.0.0.1:8188", timeout=5)
    print(" ComfyUI доступен")
except Exception as e:
    print(f" Ошибка: {e}")
    sys.exit(1)

# ПРАВИЛЬНЫЙ пайплайн для ComfyUI v0.13.0+
payload = {
    "1": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"}
    },
    "2": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "professional portrait photo of a woman, sharp eyes, natural skin texture, soft studio lighting",
            "clip": ["1", 1]  # clip = выход [1] узла 1
        }
    },
    "3": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "ugly, blurry, deformed face, bad anatomy, cartoon",
            "clip": ["1", 1]
        }
    },
    "4": {
        "class_type": "EmptyLatentImage",
        "inputs": {"width": 512, "height": 768, "batch_size": 1}
    },
    "5": {
        "class_type": "KSampler",
        "inputs": {
            "model": ["1", 0],        # model = выход [0] узла 1
            "positive": ["2", 0],
            "negative": ["3", 0],
            "latent_image": ["4", 0],
            "seed": 42,
            "steps": 20,
            "cfg": 8.0,               # Важно: число с плавающей точкой
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1.0
        }
    },
    "6": {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": ["5", 0],
            "vae": ["1", 2]           # vae = выход [2] узла 1
        }
    },
    "7": {
        "class_type": "SaveImage",
        "inputs": {
            "images": ["6", 0],
            "filename_prefix": "test_run/portrait"
        }
    }
}

print(" Отправка запроса на генерацию...")
resp = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": payload}, timeout=10)
if resp.status_code != 200:
    print(f"\n Ошибка {resp.status_code}: {resp.text[:500]}")
    sys.exit(1)

prompt_id = resp.json().get("prompt_id", "unknown")
print(f" Запрос принят (ID: {prompt_id}). Генерация ~3-5 сек...")

# Ожидание файла (путь для портативной сборки)
out_dir = Path(r"G:\1\AI\ComfyUI\ComfyUI\output\test_run")
start = time.time()
while time.time() - start < 30:
    if out_dir.exists() and any(f.endswith('.png') for f in os.listdir(out_dir)):
        pngs = sorted([f for f in os.listdir(out_dir) if f.endswith('.png')], reverse=True)
        print(f"\n УСПЕХ! Изображение сохранено:\n   {out_dir / pngs[0]}")
        print("="*60)
        sys.exit(0)
    time.sleep(0.5)
    print(".", end="", flush=True)

print("\n\n Таймаут: изображение не сгенерировано за 30 сек")
print("   Проверь лог сервера на наличие ошибок")
sys.exit(1)
