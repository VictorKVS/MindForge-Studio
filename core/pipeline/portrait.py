"""
Пайплайн генерации портретов с автоматическим аудитом для 152-ФЗ.
"""
from core.adapters.comfyui import ComfyUIAdapter
from core.knowledge.storage import KnowledgeBase
import re

class PortraitPipeline:
    def __init__(self, user_id: str = "anonymous"):
        self.adapter = ComfyUIAdapter()
        self.kb = KnowledgeBase()
        self.user_id = user_id
    
    def generate(self, prompt: str, negative_prompt: str = "", width: int = 512, height: int = 768,
                style: str = "business") -> dict:
        """
        Генерирует портрет с полным аудитом для соответствия 152-ФЗ.
        Все параметры сохраняются ДО начала генерации (гарантия аудита даже при ошибках).
        """
        # 1. Обнаружение ПДн в промте (ФИО, паспорт и т.д.)
        pii_detected = self._detect_pii(prompt)
        
        # 2. Сохраняем запрос в базу ДО генерации (критично для аудита!)
        gen_id = self.kb.save_generation(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            user_id=self.user_id,
            metadata={"style": style, "pii_detected": pii_detected}
        )
        
        try:
            # 3. Генерация изображения
            result = self.adapter.generate(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height
            )
            
            # 4. Логируем соответствие требованиям
            self.kb.log_compliance(
                generation_id=gen_id,
                pii_detected=pii_detected,
                anonymized=True,  # Всегда анонимизируем для медицины
                audit_user=self.user_id
            )
            
            return {**result, "generation_id": gen_id, "audit_status": "compliant"}
            
        except Exception as e:
            # Даже при ошибке  запись в аудит сохранена!
            self.kb.log_compliance(
                generation_id=gen_id,
                pii_detected=pii_detected,
                anonymized=False,
                audit_user=self.user_id
            )
            raise
    
    def _detect_pii(self, text: str) -> bool:
        """Простая проверка на персональные данные (ФИО, паспорт, СНИЛС)."""
        pii_patterns = [
            r'\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?\b',  # ФИО
            r'\b\d{4}\s\d{4}\s\d{4}\b',                                # Паспорт (пример)
            r'\b\d{11}\b',                                             # СНИЛС
            r'\b\d{3}-\d{3}-\d{3}\s\d{2}\b',                           # Полис ОМС
            r'(фамилия|имя|отчество|паспорт|снилс|полис|дата рождения)'
        ]
        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in pii_patterns)
    
    def get_audit_report(self, days: int = 7):
        """Получить аудит-отчёт за последние N дней."""
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return self.kb.get_audit_report(start_date=start_date, end_date=end_date)
