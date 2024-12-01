import sqlite3

conn = sqlite3.connect('finance_bot.db')
c = conn.cursor()

# Create User table
c.execute('''CREATE TABLE IF NOT EXISTS user (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    budget REAL DEFAULT 0,
    balance REAL DEFAULT 0
);''')

# Create UserTransaction table
c.execute('''
CREATE TABLE IF NOT EXISTS UserTransaction (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    transaction_type TEXT CHECK(transaction_type IN ('income', 'expense')),
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (user_id)
);
''')

c.execute('''
CREATE TRIGGER IF NOT EXISTS update_balance_after_transaction
AFTER INSERT ON UserTransaction
BEGIN
    UPDATE user
    SET balance = CASE
        WHEN NEW.transaction_type = 'income' THEN balance + NEW.amount
        WHEN NEW.transaction_type = 'expense' THEN balance - NEW.amount
    END
    WHERE user_id = NEW.user_id;
END;
''')

# Create Report table
c.execute('''CREATE TABLE IF NOT EXISTS report (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total_income REAL NOT NULL DEFAULT 0.0,
    total_expense REAL NOT NULL DEFAULT 0.0,
    balance REAL NOT NULL DEFAULT 0.0,
    start_period DATE NOT NULL,
    end_period DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE
);''')



# Create RecurringTransaction table
#comming soon
""" c.execute('''CREATE TABLE IF NOT EXISTS RecurringTransaction (
    recurring_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    transaction_type TEXT CHECK(transaction_type IN ('income', 'expense')),
    interval TEXT CHECK(interval IN ('day', 'week', '2 weeks', 'month')),
    next_due_date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (user_id)
);
''') """



conn.commit()
conn.close()