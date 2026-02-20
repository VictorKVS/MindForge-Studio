"""
Шаблоны промптов для коммерческой генерации.
Каждый шаблон оптимизирован для конкретного типа контента.
"""
from typing import Dict, Any

class PromptTemplates:
    """Коллекция готовых шаблонов промптов."""
    
    @staticmethod
    def business_portrait(gender: str = "woman", style: str = "professional") -> Dict[str, Any]:
        """Бизнес-портрет для сайтов, LinkedIn, рекламы."""
        prompts = {
            "woman": {
                "professional": "professional business portrait of a confident woman in elegant suit, studio lighting, sharp focus, natural expression, corporate style",
                "friendly": "friendly business woman smiling, approachable corporate portrait, soft lighting, modern office background",
                "executive": "executive business woman in power suit, confident leadership portrait, professional studio lighting"
            },
            "man": {
                "professional": "professional business portrait of a confident man in tailored suit, studio lighting, sharp focus, natural expression, corporate style",
                "friendly": "friendly business man smiling, approachable corporate portrait, soft lighting, modern office background",
                "executive": "executive business man in power suit, confident leadership portrait, professional studio lighting"
            }
        }
        return {
            "prompt": prompts[gender][style],
            "negative_prompt": "ugly, blurry, deformed face, cartoon, anime, bad anatomy, extra limbs",
            "width": 1024,
            "height": 1024,
            "model": "sd_xl_base_1.0.safetensors",
            "lora": "Headshot.safetensors",
            "lora_weight": 0.8,
            "category": "business",
            "use_case": "website, linkedin, corporate"
        }
    
    @staticmethod
    def medical_portrait(role: str = "doctor", gender: str = "woman") -> Dict[str, Any]:
        """Медицинский портрет для клиник, статей, сайтов."""
        prompts = {
            "doctor": {
                "woman": "professional female doctor in white coat, stethoscope, confident medical portrait, clean background, clinical lighting",
                "man": "professional male doctor in white coat, stethoscope, confident medical portrait, clean background, clinical lighting"
            },
            "nurse": {
                "woman": "friendly female nurse smiling, professional healthcare portrait, white uniform, caring expression",
                "man": "friendly male nurse smiling, professional healthcare portrait, white uniform, caring expression"
            },
            "specialist": {
                "woman": "medical specialist in lab coat, professional portrait, scientific background, expert expression",
                "man": "medical specialist in lab coat, professional portrait, scientific background, expert expression"
            }
        }
        return {
            "prompt": prompts[role][gender],
            "negative_prompt": "ugly, blurry, deformed face, blood, gore, cartoon, unprofessional",
            "width": 1024,
            "height": 1024,
            "model": "sd_xl_base_1.0.safetensors",
            "lora": "Headshot.safetensors",
            "lora_weight": 0.7,
            "category": "medical",
            "use_case": "clinic website, medical articles, healthcare"
        }
    
    @staticmethod
    def creative_portrait(style: str = "artistic") -> Dict[str, Any]:
        """Креативный портрет для обложек, арта, соцсетей."""
        prompts = {
            "artistic": "artistic portrait, dramatic lighting, creative composition, fine art photography, unique expression",
            "cinematic": "cinematic portrait, movie still style, dramatic shadows, film lighting, professional actor",
            "fantasy": "fantasy character portrait, magical lighting, ethereal atmosphere, detailed costume, otherworldly",
            "retro": "vintage portrait, retro 70s style, warm tones, classic photography, nostalgic mood"
        }
        return {
            "prompt": prompts[style],
            "negative_prompt": "ugly, blurry, deformed face, modern, contemporary, amateur",
            "width": 1024,
            "height": 1024,
            "model": "sd_xl_base_1.0.safetensors",
            "lora": "midjourney-studio-light.safetensors",
            "lora_weight": 0.9,
            "category": "creative",
            "use_case": "book covers, social media, art projects"
        }
    
    @staticmethod
    def banner(width: int = 1920, height: int = 1080, theme: str = "business") -> Dict[str, Any]:
        """Баннер для сайта, соцсетей, рекламы."""
        prompts = {
            "business": "professional business banner, modern office, people collaborating, clean design, corporate colors",
            "medical": "healthcare banner, medical professionals, clean hospital environment, trust and care theme",
            "creative": "creative agency banner, artistic design, bold colors, modern typography, innovative vibe"
        }
        return {
            "prompt": prompts[theme],
            "negative_prompt": "ugly, blurry, cluttered, amateur design, poor composition",
            "width": width,
            "height": height,
            "model": "sd_xl_base_1.0.safetensors",
            "lora": None,
            "category": "banner",
            "use_case": "website header, social media, advertising"
        }
    
    @staticmethod
    def website_section(section_type: str = "hero") -> Dict[str, Any]:
        """Секция для сайта (герой, услуги, команда)."""
        prompts = {
            "hero": "hero section background, modern design, professional atmosphere, clean and inviting",
            "team": "team section background, collaborative workspace, diverse professionals, friendly environment",
            "services": "services section background, professional icons, clean layout, corporate style"
        }
        return {
            "prompt": prompts[section_type],
            "negative_prompt": "ugly, blurry, cluttered, amateur, poor design",
            "width": 1920,
            "height": 800,
            "model": "sd_xl_base_1.0.safetensors",
            "lora": None,
            "category": "website",
            "use_case": "web design, figma export"
        }
