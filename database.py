import sqlite3

DB_NAME = "finance.db"

# 🔹 Create database connection
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # return rows as dictionary
    return conn