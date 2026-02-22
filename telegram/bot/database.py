# ========================================
# Database Module v2.0
# С статистикой пользователей
# ========================================

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import json

class BotDatabase:
    MAX_MESSAGES = 10000
    
    def __init__(self, db_path: str = "bot_database.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TEXT,
                last_seen TEXT,
                total_messages INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_text TEXT,
                message_type TEXT,
                timestamp TEXT,
                chat_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                user_id INTEGER,
                order_type TEXT,
                style TEXT,
                deadline TEXT,
                extra TEXT,
                status TEXT,
                created_at TEXT,
                yaml_path TEXT,
                file_path TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                user_id INTEGER,
                payload TEXT,
                timestamp TEXT
            )
        """)
        
        self.conn.commit()
    
    def _cleanup_old_messages(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM messages")
        count = cursor.fetchone()[0]
        
        if count > self.MAX_MESSAGES:
            to_delete = count - self.MAX_MESSAGES + 1000
            cursor.execute("""
                DELETE FROM messages 
                WHERE id IN (
                    SELECT id FROM messages 
                    ORDER BY timestamp ASC 
                    LIMIT ?
                )
            """, (to_delete,))
            self.conn.commit()
    
    def upsert_user(self, user_id: int, username: str, first_name: str, last_name: str = None):
        cursor = self.conn.cursor()
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            INSERT INTO users (user_id, username, first_name, last_name, created_at, last_seen, total_messages)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                last_seen = excluded.last_seen,
                total_messages = total_messages + 1
        """, (user_id, username, first_name, last_name, now, now))
        
        self.conn.commit()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_stats(self, user_id: int) -> Dict:
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM messages WHERE user_id = ?", (user_id,))
        total_messages = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = ?", (user_id,))
        total_orders = cursor.fetchone()[0]
        
        return {
            "total_messages": total_messages,
            "total_orders": total_orders
        }
    
    def log_message(self, user_id: int, message_text: str, message_type: str, chat_id: int):
        cursor = self.conn.cursor()
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            INSERT INTO messages (user_id, message_text, message_type, timestamp, chat_id)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, message_text, message_type, now, chat_id))
        
        self.conn.commit()
        self._cleanup_old_messages()
    
    def get_user_messages(self, user_id: int, limit: int = 50) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM messages 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (user_id, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def create_order(self, order_id: str, user_id: int, order_data: Dict, yaml_path: str):
        cursor = self.conn.cursor()
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            INSERT INTO orders (order_id, user_id, order_type, style, deadline, extra, status, created_at, yaml_path, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_id,
            user_id,
            order_data.get('type'),
            order_data.get('style'),
            order_data.get('deadline', {}).get('raw'),
            order_data.get('extra'),
            'confirmed',
            now,
            yaml_path,
            order_data.get('file_path')
        ))
        
        self.conn.commit()
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_user_orders(self, user_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM orders 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (user_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_order_status(self, order_id: str, status: str):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE orders SET status = ? WHERE order_id = ?
        """, (status, order_id))
        self.conn.commit()
    
    def log_event(self, event_type: str, user_id: int, payload: Dict):
        cursor = self.conn.cursor()
        now = datetime.utcnow().isoformat()
        
        cursor.execute("""
            INSERT INTO events (event_type, user_id, payload, timestamp)
            VALUES (?, ?, ?, ?)
        """, (event_type, user_id, json.dumps(payload, ensure_ascii=False), now))
        
        self.conn.commit()
    
    def get_stats(self) -> Dict:
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM messages")
        total_messages = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'confirmed'")
        confirmed_orders = cursor.fetchone()[0]
        
        return {
            "total_users": total_users,
            "total_messages": total_messages,
            "total_orders": total_orders,
            "confirmed_orders": confirmed_orders,
            "messages_limit": self.MAX_MESSAGES,
            "messages_usage_percent": round(total_messages / self.MAX_MESSAGES * 100, 2)
        }
    
    def close(self):
        self.conn.close()

_db_instance = None

def get_database() -> BotDatabase:
    global _db_instance
    if _db_instance is None:
        _db_instance = BotDatabase()
    return _db_instance

