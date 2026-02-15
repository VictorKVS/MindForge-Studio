import os
import requests
from pathlib import Path
from typing import Dict, Any
import time
import base64
import io
from PIL import Image


class SDForgeAdapter:
    name = "sd_forge"
    
    def __init__(
        self,
        base_url: str = None,
        output_dir: str = "outputs/portraits",
        timeout: int = 300
    ):
        self.base_url = (base_url or os.getenv("SD_FORGE_URL", "http://127.0.0.1:7860")).rstrip("/")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
    
    def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Минимальный рабочий массив данных для интерфейса Forge
        data = [
            payload["prompt"],                          # 0: prompt
            payload.get("negative_prompt", ""),         # 1: negative_prompt
            payload.get("sampler_name", "DPM++ 2M Karras"),  # 2: sampler
            payload.get("steps", 22),                   # 3: steps
            payload.get("cfg_scale", 6.0),              # 4: cfg_scale
            payload.get("seed", -1),                    # 5: seed
            -1,                                         # 6: batch_size
            1,                                          # 7: n_iter
            payload.get("width", 512),                  # 8: width
            payload.get("height", 640),                 # 9: height
            False,                                      # 10: restore_faces
            False,                                      # 11: tiling
            0,                                          # 12: hires_steps
            0,                                          # 13: denoising_strength
            0,                                          # 14: first_pass_width
            0,                                          # 15: first_pass_height
            "Latent",                                   # 16: resize_mode
            0,                                          # 17: refiner_switch_at
            "",                                         # 18: refiner_checkpoint
            "",                                         # 19: secondary_prompt
            "",                                         # 20: secondary_negative_prompt
            "",                                         # 21: scripts
            "",                                         # 22: script_args
            "",                                         # 23: style
            "",                                         # 24: style2
            "",                                         # 25: lora
            "",                                         # 26: lora_strength
            "",                                         # 27: extra networks
            "",                                         # 28: hires_prompt
            "",                                         # 29: hires_negative_prompt
        ]
        
        start_time = time.time()
        try:
            resp = requests.post(
                f"{self.base_url}/run/predict",
                json={
                    "data": data,
                    "session_hash": f"mindforge_{int(time.time())}"
                },
                timeout=self.timeout
            )
            resp.raise_for_status()
            result = resp.json()
            
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Генерация превысила лимит {self.timeout} сек")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ошибка Forge API: {e}")
        
        # Извлекаем изображение из ответа Gradio
        if "data" not in result or len(result["data"]) == 0:
            raise RuntimeError(f"Forge вернул пустой результат. Ответ: {result}")
        
        image_b64 = result["data"][0]
        if not image_b64 or "data:image" not in image_b64:
            raise RuntimeError(f"Некорректный формат изображения. Данные: {image_b64[:100]}")
        
        # Декодируем и сохраняем
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]
        
        try:
            image_data = base64.b64decode(image_b64)
            img = Image.open(io.BytesIO(image_data))
        except Exception as e:
            raise RuntimeError(f"Ошибка декодирования изображения: {e}. Данные: {image_b64[:100]}...")
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"portrait_{timestamp}.png"
        filepath = self.output_dir / filename
        img.save(filepath, "PNG")
        
        generation_time = time.time() - start_time
        
        return {
            "images": [str(filepath.absolute())],
            "meta": {
                "seed": payload.get("seed", -1),
                "steps": payload.get("steps", 22),
                "cfg_scale": payload.get("cfg_scale", 6.0),
                "width": payload.get("width", 512),
                "height": payload.get("height", 640),
                "sampler": payload.get("sampler_name", "DPM++ 2M Karras"),
                "model": "v1-5-pruned-emaonly",
                "generation_time_sec": round(generation_time, 2),
                "backend": self.name
            }
        }