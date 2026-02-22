async def get_available_lessons():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            '''
            SELECT *
            FROM lessons
            WHERE is_available = 1
            ORDER BY date, time
            '''
        ) as cursor:
            return await cursor.fetchall()