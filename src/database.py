import aiosqlite
import asyncio
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS blacklist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT UNIQUE NOT NULL
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    description TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    guild_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    PRIMARY KEY (guild_id, key)
                )
            ''')
            await db.commit()

    async def get_blacklist(self):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('SELECT word FROM blacklist')
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def add_blacklist_word(self, word):
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute('INSERT INTO blacklist (word) VALUES (?)', (word,))
                await db.commit()
                return True
            except aiosqlite.IntegrityError:
                return False

    async def remove_blacklist_word(self, word):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM blacklist WHERE word = ?', (word,))
            await db.commit()

    async def log_event(self, guild_id, event_type, description):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('INSERT INTO events (guild_id, event_type, description) VALUES (?, ?, ?)',
                             (guild_id, event_type, description))
            await db.commit()

    async def log_action(self, user_id, guild_id, action_type):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('INSERT INTO actions (user_id, guild_id, action_type) VALUES (?, ?, ?)',
                             (user_id, guild_id, action_type))
            await db.commit()

    async def get_actions(self, user_id, guild_id, action_type, time_window_minutes):
        since = datetime.now() - timedelta(minutes=time_window_minutes)
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT COUNT(*) FROM actions
                WHERE user_id = ? AND guild_id = ? AND action_type = ? AND timestamp > ?
            ''', (user_id, guild_id, action_type, since))
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def set_config(self, guild_id, key, value):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO config (guild_id, key, value) VALUES (?, ?, ?)
            ''', (guild_id, key, value))
            await db.commit()
