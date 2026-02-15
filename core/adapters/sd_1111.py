# core/adapters/sd_1111.py
import base64
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


@dataclass
class SD1111Adapter:
    base_url: str
    timeout: int = 600  # сек

    def txt2img(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}/sdapi/v1/txt2img"
        r = requests.post(url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def save_base64_png(b64: str, out_path: str) -> str:
        # b64 может быть с префиксом "data:image/png;base64,"
        if "," in b64:
            b64 = b64.split(",", 1)[1]
        data = base64.b64decode(b64)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(data)
        return out_path

    def generate_and_save(self, payload: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        resp = self.txt2img(payload)
        images = resp.get("images", [])
        ts = time.strftime("%Y%m%d_%H%M%S")

        saved = []
        for i, b64 in enumerate(images):
            out_path = os.path.join(output_dir, f"portrait_{ts}_{i:02d}.png")
            saved.append(self.save_base64_png(b64, out_path))

        return {
            "images": saved,
            "info": resp.get("info"),
            "parameters": resp.get("parameters"),
        }
