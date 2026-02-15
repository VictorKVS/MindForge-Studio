# core/pipeline/portrait.py
import yaml
from core.adapters.sd_1111 import SD1111Adapter
from pathlib import Path

class PortraitPipeline:

    def __init__(self):
        self.adapter = SD1111Adapter()

    def run_from_order(self, order_path: str):

        with open(order_path, "r", encoding="utf-8") as f:
            order = yaml.safe_load(f)

        subject = order["subject"]
        style = order["style"]
        comp = order["composition"]
        output = order["output"]

        prompt = (
            f"{style['base']}, {style['mood']}, "
            f"{subject['gender']} {subject['age']} years old, "
            f"{subject['ethnicity']} woman, {subject['hair']} hair, "
            f"{subject['eyes']} eyes, {subject['skin']}, "
            f"{style['lighting']}, {style['background']}, "
            f"{comp['camera']}, {comp['framing']}, {comp['angle']}, "
            f"ultra detailed, sharp focus, professional photography"
        )

        negative = "blurry, low quality, deformed face, extra fingers, bad anatomy"

        results = []

        for i in range(output["count"]):
            payload = {
                "prompt": prompt,
                "negative_prompt": negative,
                "steps": output["steps"],
                "cfg_scale": output["cfg"],
                "sampler_name": output["sampler"],
                "width": output["width"],
                "height": output["height"],
                "seed": output["seed"] + i
            }

            r = self.adapter.generate(payload)
            results.append(r["images"][0])

        return results
