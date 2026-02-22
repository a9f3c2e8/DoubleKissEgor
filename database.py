import aiosqlite
import os
from datetime import datetime
from config import DB_PATH

async def init_db():
    if not os.path.exists(DB_PATH):
        print(f"WARNING: Database file not found at {DB_PATH}, creating...")
        open(DB_PATH, 'w').close()  # Создаем файл, если его нет

    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            await db.execute('''
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    duration INTEGER DEFAULT 60,
                    price INTEGER NOT NULL,
                    description TEXT,
                    is_available INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            await db.execute('''
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    lesson_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (lesson_id) REFERENCES lessons (id)
                )
            ''')

            await db.commit()
            print("Database initialized successfully")
    except Exception as e:
        print(f"Error during database initialization: {e}")