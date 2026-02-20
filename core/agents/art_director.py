# ========================================
# Название: Art Director Agent
# Описание: LLM-агент для сборки промптов
# Версия: 1.0.0
# ========================================

import sys
import os
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class KnowledgeBase:
    """Загрузка базы знаний из YAML"""
    
    def __init__(self, knowledge_path="knowledge"):
        self.knowledge_path = knowledge_path
        self.emotions = self._load_yaml("emotions.yaml")
        self.styles = self._load_yaml("styles.yaml")
        self.poses = self._load_yaml("poses.yaml")
        self.lighting = self._load_yaml("lighting.yaml")
        self.models = self._load_yaml("models.yaml")
    
    def _load_yaml(self, filename):
        filepath = os.path.join(self.knowledge_path, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf8') as f:
                return yaml.safe_load(f)
        return {}
    
    def get_style_prompt(self, style_name):
        style = self.styles.get(style_name, {})
        return style.get("prompt", "")
    
    def get_emotion_tokens(self, emotion_name):
        emotion = self.emotions.get(emotion_name, {})
        return emotion.get("tokens", [])
    
    def get_pose_tokens(self, pose_name):
        pose = self.poses.get(pose_name, {})
        return pose.get("tokens", [])
    
    def get_lighting_tokens(self, lighting_name):
        lighting = self.lighting.get(lighting_name, {})
        return lighting.get("tokens", [])
    
    def get_model_config(self, style_name):
        model_map = {
            "business": "portrait_base",
            "cinematic": "cinematic_xl",
            "fantasy": "fantasy_art",
            "fashion": "fashion_pro"
        }
        model_key = model_map.get(style_name, "portrait_base")
        return self.models.get(model_key, {})


class ArtDirectorAgent:
    """LLM-агент для сборки финального промпта"""
    
    def __init__(self):
        self.kb = KnowledgeBase()
    
    def assemble_prompt(self, order):
        style_prompt = self.kb.get_style_prompt(order.get("style", "business"))
        emotion_tokens = self.kb.get_emotion_tokens(order.get("emotion", "neutral"))
        pose_tokens = self.kb.get_pose_tokens(order.get("pose", "front_facing"))
        lighting_tokens = self.kb.get_lighting_tokens(order.get("lighting", "studio"))
        
        prompt_parts = [
            style_prompt,
            order.get("subject", "portrait"),
            ", ".join(emotion_tokens),
            ", ".join(pose_tokens),
            ", ".join(lighting_tokens)
        ]
        
        final_prompt = ", ".join([p for p in prompt_parts if p])
        model_config = self.kb.get_model_config(order.get("style", "business"))
        
        return {
            "prompt": final_prompt,
            "negative": self.kb.styles.get(order.get("style", "business"), {}).get("negative", ""),
            "cfg": model_config.get("cfg", 5.5),
            "steps": model_config.get("steps", 25),
            "resolution": model_config.get("resolution", "512x512"),
            "model_config": model_config
        }
    
    def process_order(self, order):
        print("=" * 60)
        print(" ART DIRECTOR  Сборка промпта")
        print("=" * 60)
        print(f" Заказ: {order}")
        
        result = self.assemble_prompt(order)
        
        print(f" Prompt: {result['prompt'][:100]}...")
        print(f" Negative: {result['negative'][:50]}...")
        print(f"  CFG: {result['cfg']}, Steps: {result['steps']}")
        print(f" Resolution: {result['resolution']}")
        print("=" * 60)
        
        return result


if __name__ == "__main__":
    agent = ArtDirectorAgent()
    
    test_order = {
        "style": "business",
        "emotion": "confidence",
        "pose": "three_quarter",
        "lighting": "studio",
        "subject": "professional woman in elegant suit"
    }
    
    result = agent.process_order(test_order)
