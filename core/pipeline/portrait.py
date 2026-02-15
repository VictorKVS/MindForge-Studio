from pathlib import Path
from typing import Dict, Any, Optional
from core.adapters.sd_forge import SDForgeAdapter


class PortraitPipeline:
    def __init__(
        self,
        backend: str = "sd_forge",
        output_dir: str = "outputs/portraits",
        **kwargs
    ):
        self.backend = backend
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if backend in ("sd_forge", "forge", "sd-1111", "sd_1111"):
            self.adapter = SDForgeAdapter(
                base_url=None,
                output_dir=str(self.output_dir)
            )
        else:
            raise ValueError(f"Неизвестный backend: {backend}")
    
    def generate(
        self,
        prompt: str,
        negative_prompt: str = "low quality, blurry, deformed face, bad anatomy, plastic skin",
        steps: int = 22,
        cfg_scale: float = 6.0,
        width: int = 512,
        height: int = 640,
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "seed": seed if seed is not None else -1,
            "sampler_name": "DPM++ 2M Karras",
        }
        
        result = self.adapter.generate(payload)
        
        return {
            "images": result["images"],
            "meta": {
                **result["meta"],
                "prompt": prompt,
                "style": self._detect_style(prompt),
                "pipeline": "portrait_v1",
                "backend": self.backend
            }
        }
    
    def _detect_style(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "cinematic" in prompt_lower or "film" in prompt_lower:
            return "cinematic"
        elif "linkedin" in prompt_lower or "professional" in prompt_lower:
            return "linkedin"
        elif "avatar" in prompt_lower:
            return "avatar"
        elif "tech" in prompt_lower or "architect" in prompt_lower:
            return "tech"
        return "default"