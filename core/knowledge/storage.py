"""
База знаний для генерации портретов  аудит + шаблоны + поиск.
Соответствует требованиям 152-ФЗ / 187-ФЗ для медицинских приложений.
"""
import sqlite3
from pathlib import Path
import json
import hashlib
from datetime import datetime, timedelta  #  Добавили timedelta

class KnowledgeBase:
    def __init__(self, db_path: str = "data/knowledge.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Создаёт таблицы при первом запуске."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generations (
                id TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                prompt TEXT NOT NULL,
                negative_prompt TEXT,
                seed INTEGER,
                width INTEGER,
                height INTEGER,
                model TEXT,
                image_path TEXT,
                user_id TEXT,
                session_id TEXT,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compliance_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                generation_id TEXT NOT NULL,
                pii_detected BOOLEAN DEFAULT FALSE,
                anonymized BOOLEAN DEFAULT FALSE,
                audit_user TEXT,
                retention_until DATETIME,
                FOREIGN KEY(generation_id) REFERENCES generations(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_generations_timestamp ON generations(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_generations_user ON generations(user_id)")
        
        conn.commit()
        conn.close()
    
    def save_generation(self, prompt: str, negative_prompt: str = "", seed: int = None,
                       width: int = 512, height: int = 768, model: str = "sd15",
                       image_path: str = "", user_id: str = "anonymous", session_id: str = None,
                       metadata: dict = None) -> str:
        """Сохраняет генерацию в базу (для аудита)."""
        timestamp = datetime.now().isoformat()
        gen_id = hashlib.sha256(f"{prompt}{seed}{width}{height}{timestamp}".encode()).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO generations 
            (id, prompt, negative_prompt, seed, width, height, model, image_path, user_id, session_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            gen_id,
            prompt[:1000],
            negative_prompt[:1000],
            seed,
            width,
            height,
            model,
            str(image_path),
            user_id,
            session_id or hashlib.sha256(f"{user_id}{timestamp}".encode()).hexdigest()[:12],
            json.dumps(metadata or {}, ensure_ascii=False)
        ))
        
        conn.commit()
        conn.close()
        return gen_id
    
    def log_compliance(self, generation_id: str, pii_detected: bool = False, anonymized: bool = True,
                      audit_user: str = "system", retention_days: int = 90):
        """Логирует действия по защите ПДн для 152-ФЗ."""
        retention_until = (datetime.now() + timedelta(days=retention_days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO compliance_log 
            (generation_id, pii_detected, anonymized, audit_user, retention_until)
            VALUES (?, ?, ?, ?, ?)
        """, (
            generation_id,
            1 if pii_detected else 0,
            1 if anonymized else 0,
            audit_user,
            retention_until
        ))
        
        conn.commit()
        conn.close()
    
    def get_audit_report(self, start_date: str = None, end_date: str = None, user_id: str = None) -> list:
        """Генерирует отчёт для аудита (152-ФЗ, 187-ФЗ)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT g.timestamp, g.user_id, g.prompt, g.model, c.pii_detected, c.anonymized
            FROM generations g
            LEFT JOIN compliance_log c ON g.id = c.generation_id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND DATE(g.timestamp) >= ?"
            params.append(start_date)
        if end_date:
            query += " AND DATE(g.timestamp) <= ?"
            params.append(end_date)
        if user_id:
            query += " AND g.user_id = ?"
            params.append(user_id)
        
        query += " ORDER BY g.timestamp DESC LIMIT 1000"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "timestamp": r[0],
                "user_id": r[1],
                "prompt": r[2][:100] + "..." if len(r[2]) > 100 else r[2],
                "model": r[3],
                "pii_detected": bool(r[4]) if r[4] is not None else False,
                "anonymized": bool(r[5]) if r[5] is not None else False
            }
            for r in results
        ]
