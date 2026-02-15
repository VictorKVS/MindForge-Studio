import requests
import time
from pathlib import Path
from typing import Dict, Any, Optional
class ComfyUIAdapter:
def init(self, host: str = "127.0.0.1", port: int = 8188, model: str = "v1-5-pruned-emaonly.safetensors"):
self.url = f"http://{host}:{port}"
self.model = model
self.output_dir = Path(r"G:\1\AI\ComfyUI\ComfyUI\output")
def _build_pipeline(self, prompt: str, negative_prompt: str, width: int = 512, height: int = 768, seed: int = 42):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": self.model}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": negative_prompt, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0],
            "seed": seed, "steps": 20, "cfg": 8.0, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0
        }},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "test_run/portrait"}}
    }

def generate(self, prompt: str, negative_prompt: str = "ugly, blurry, deformed face", width: int = 512, height: int = 768) -> Dict[str, Any]:
    pipeline = self._build_pipeline(prompt, negative_prompt, width, height)
    resp = requests.post(f"{self.url}/prompt", json={"prompt": pipeline}, timeout=30)
    resp.raise_for_status()
    
    # Wait for image
    out_dir = self.output_dir / "test_run"
    for _ in range(60):
        if out_dir.exists():
            pngs = sorted([f for f in out_dir.glob("*.png")], key=lambda x: x.stat().st_mtime, reverse=True)
            if pngs:
                return {"success": True, "image_path": str(pngs[0]), "generation_time_sec": 3.5}
        time.sleep(0.5)
    raise TimeoutError("Image not generated in 30 seconds")
