"""llm/
 └── agents/
     ├── art_director.py   ← 🧠 LLM-агент
     ├── schemas.py        ← Pydantic-схемы решений
     └── prompts/
         └── art_director.system.md
🧠 1. Схема решения (строго!)

llm/agents/schemas.py

"""

from pydantic import BaseModel
from typing import Literal

class PortraitDecision(BaseModel):
    style: Literal["cinematic", "linkedin", "avatar"]
    prompt: str
    negative_prompt: str
    steps: int
    cfg_scale: float
    width: int
    height: int
    seed: int
