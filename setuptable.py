from app.db import get_db

conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash BLOB NOT NULL
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    category TEXT,
    exercise TEXT,
    sets INTEGER,
    reps INTEGER,
    weight REAL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.execute("""
ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0
""")

conn.execute("""
ALTER TABLE users ADD COLUMN level INTEGER DEFAULT 1
""")

conn.commit()

conn.close()