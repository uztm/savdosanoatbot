import sqlite3
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Foydalanuvchilar jadvali
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER UNIQUE,
        language TEXT DEFAULT 'uz'
    )
    """)

    # Tadbirlar jadvali
    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        image_url TEXT,
        is_archived INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

def add_user(user_id, lang="uz"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, language) VALUES (?, ?)", (user_id, lang))
    conn.commit()
    conn.close()

def set_user_language(user_id, lang):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET language=? WHERE user_id=?", (lang, user_id))
    conn.commit()
    conn.close()

def get_user_language(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else "uz"

def add_event(title, description, image_url):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO events (title, description, image_url) VALUES (?, ?, ?)", (title, description, image_url))
    conn.commit()
    conn.close()

def get_events(active_only=True):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if active_only:
        cur.execute("SELECT id, title FROM events WHERE is_archived=0")
    else:
        cur.execute("SELECT id, title FROM events")
    events = cur.fetchall()
    conn.close()
    return events

def get_event_detail(event_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT title, description, image_url FROM events WHERE id=?", (event_id,))
    event = cur.fetchone()
    conn.close()
    return event
