import aiosqlite
from typing import Optional, List, Tuple
from datetime import datetime

from config import config


class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DB_PATH
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self):
        
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self._connection = await aiosqlite.connect(self.db_path)
        await self._create_tables()

    async def disconnect(self):
        
        if self._connection:
            await self._connection.close()

    async def _create_tables(self):
        
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                generations_count INTEGER DEFAULT 0
            )
        """)

        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        await self._connection.execute("""
            INSERT OR IGNORE INTO settings (key, value) VALUES ('bot_access', 'open')
        """)

        await self._connection.commit()

    async def add_user(self, user_id: int, username: str = None,
                       first_name: str = None, last_name: str = None) -> bool:
        
        try:
            await self._connection.execute("""
                INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, first_name, last_name))
            await self._connection.commit()
            return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False

    async def get_user(self, user_id: int) -> Optional[Tuple]:
        
        async with self._connection.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            return await cursor.fetchone()

    async def get_all_users(self) -> List[Tuple]:
        
        async with self._connection.execute(
                "SELECT user_id, username, first_name, last_name, created_at, generations_count FROM users"
        ) as cursor:
            return await cursor.fetchall()

    async def get_users_count(self) -> int:
        
        async with self._connection.execute("SELECT COUNT(*) FROM users") as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def increment_generations(self, user_id: int):
        
        await self._connection.execute("""
            UPDATE users SET generations_count = generations_count + 1 WHERE user_id = ?
        """, (user_id,))
        await self._connection.commit()

    async def get_bot_access(self) -> bool:
        
        async with self._connection.execute(
                "SELECT value FROM settings WHERE key = 'bot_access'"
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] == 'open' if result else True

    async def set_bot_access(self, is_open: bool):
        
        value = 'open' if is_open else 'closed'
        await self._connection.execute("""
            UPDATE settings SET value = ? WHERE key = 'bot_access'
        """, (value,))
        await self._connection.commit()
db = Database()