import yaml
import random

class ArtDirectorAgent:
    def __init__(self, styles_path: str):
        with open(styles_path, "r", encoding="utf-8") as f:
            self.styles = yaml.safe_load(f)

    def decide(self, user_intent: str | None = None) -> dict:
        """
        Решает стиль, LoRA и параметры.
        Пока v1 — rule-based.
        Позже заменим на LLM.
        """

        if user_intent and user_intent in self.styles:
            style_name = user_intent
        else:
            style_name = random.choice(list(self.styles.keys()))

        style = self.styles[style_name]

        return {
            "style": style_name,
            "prompt": style["description"],
            "loras": style.get("loras", []),
            "cfg": style.get("cfg", 6),
            "steps": style.get("steps", 20),
        }
