import requests, json, time, os, sys

print("="*60)
print(" Генерация через стабильный API Forge (/sdapi/v1/txt2img)")
print("="*60)

payload = {
    "prompt": "professional portrait photo of a woman, sharp eyes, natural skin texture, studio lighting",
    "negative_prompt": "ugly, blurry, deformed face, cartoon",
    "width": 512,
    "height": 768,
    "steps": 25,
    "cfg_scale": 7.5,
    "seed": 42,
    "batch_size": 1,
    "n_iter": 1,
    "do_not_save_samples": False,
    "do_not_save_grid": False,
    "restore_faces": False,
    "tiling": False,
    "enable_hr": False
}

try:
    resp = requests.post(
        "http://127.0.0.1:7860/sdapi/v1/txt2img",
        json=payload,
        timeout=60
    )
    resp.raise_for_status()
    
    result = resp.json()
    image_b64 = result["images"][0]
    
    # Сохраняем
    import base64
    from pathlib import Path
    out_dir = Path("outputs/test_run")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"forge_portrait_{int(time.time())}.png"
    
    with open(path, "wb") as f:
        f.write(base64.b64decode(image_b64.split(",", 1)[-1]))
    
    print(f"\n УСПЕХ! Изображение сохранено:\n   {path.resolve()}")
    print("="*60)
    
except Exception as e:
    print(f"\n ОШИБКА: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"   Ответ сервера: {e.response.text[:500]}")
    sys.exit(1)
