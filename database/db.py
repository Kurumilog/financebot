import aiosqlite

async def add_user(user_id, first_name, budget, balance):
    async with aiosqlite.connect("finance_bot.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                budget REAL DEFAULT 0,
                balance REAL DEFAULT 0
            )
        """)
        await db.execute("""
            INSERT OR REPLACE INTO User (user_id, first_name, budget, balance)
            VALUES (?, ?, ?, ?)
        """, (user_id, first_name, budget, balance))
        await db.commit()
