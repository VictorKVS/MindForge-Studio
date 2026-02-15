# core/schemas/generation.py

def build_txt2img_payload(cfg: dict) -> dict:
    return {
        "prompt": cfg["prompt"],
        "negative_prompt": cfg["negative_prompt"],
        "steps": cfg["steps"],
        "sampler_name": cfg["sampler_name"],
        "cfg_scale": cfg["cfg_scale"],
        "width": cfg["width"],
        "height": cfg["height"],
        "seed": cfg["seed"],
    }
