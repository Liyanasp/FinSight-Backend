from database import get_db_connection

# 🔹 Create all required tables
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # ---------------- USERS TABLE ----------------
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        role TEXT CHECK(role IN ('admin', 'analyst', 'viewer')) NOT NULL,
        status TEXT CHECK(status IN ('active', 'inactive')) DEFAULT 'active'
    )
    ''')

    # ---------------- RECORDS TABLE ----------------
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL CHECK(amount > 0),
        type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
        category TEXT,
        date TEXT,
        note TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    conn.commit()
    conn.close()