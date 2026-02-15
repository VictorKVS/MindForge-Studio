# llm/tools/prompt_loader.py

import yaml
from pathlib import Path

PROMPT_FILE = Path("llm/prompts/portrait.yaml")

def load_portrait_preset(style: str) -> dict:
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if style not in data:
        style = "cinematic"

    return data[style]
