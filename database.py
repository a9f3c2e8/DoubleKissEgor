import aiosqlite
from datetime import datetime
from config import DB_PATH

async def init_db():
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

async def register_user(user_id, first_name, last_name, phone, gender, age):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?, ?, ?)',
            (user_id, first_name, last_name, phone, gender, age, datetime.now())
        )
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchone()

async def add_lesson(date, time, duration, price, description):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'INSERT INTO lessons (date, time, duration, price, description) VALUES (?, ?, ?, ?, ?)',
            (date, time, duration, price, description)
        )
        await db.commit()
        return cursor.lastrowid

async def get_available_lessons():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            'SELECT * FROM lessons WHERE is_available = 1 ORDER BY date, time'
        ) as cursor:
            return await cursor.fetchall()

async def get_lesson(lesson_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT * FROM lessons WHERE id = ?', (lesson_id,)) as cursor:
            return await cursor.fetchone()

async def book_lesson(user_id, lesson_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO bookings (user_id, lesson_id) VALUES (?, ?)',
            (user_id, lesson_id)
        )
        await db.execute('UPDATE lessons SET is_available = 0 WHERE id = ?', (lesson_id,))
        await db.commit()

async def get_user_bookings(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT b.id, l.date, l.time, l.duration, l.price, l.description, b.status
            FROM bookings b
            JOIN lessons l ON b.lesson_id = l.id
            WHERE b.user_id = ?
            ORDER BY l.date DESC, l.time DESC
        ''', (user_id,)) as cursor:
            return await cursor.fetchall()

async def update_lesson(lesson_id, date=None, time=None, duration=None, price=None, description=None):
    async with aiosqlite.connect(DB_PATH) as db:
        updates = []
        params = []
        if date: updates.append('date = ?'); params.append(date)
        if time: updates.append('time = ?'); params.append(time)
        if duration: updates.append('duration = ?'); params.append(duration)
        if price: updates.append('price = ?'); params.append(price)
        if description: updates.append('description = ?'); params.append(description)
        
        if updates:
            params.append(lesson_id)
            await db.execute(f'UPDATE lessons SET {", ".join(updates)} WHERE id = ?', params)
            await db.commit()

async def delete_lesson(lesson_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM lessons WHERE id = ?', (lesson_id,))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT * FROM users') as cursor:
            return await cursor.fetchall()

async def get_all_bookings():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT b.id, u.first_name, u.last_name, u.phone, l.date, l.time, l.price, b.status
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN lessons l ON b.lesson_id = l.id
            ORDER BY l.date DESC, l.time DESC
        ''') as cursor:
            return await cursor.fetchall()
