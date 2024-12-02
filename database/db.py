import aiosqlite
import sqlite3

DATABASE_PATH = 'finance_bot.db'


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
    
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_transactions(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM UserTransaction WHERE user_id = ?', (user_id,))
    transactions = c.fetchall()
    conn.close()
    return transactions