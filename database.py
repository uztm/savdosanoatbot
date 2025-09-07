import sqlite3
from config import DB_PATH
from typing import List, Tuple, Optional
import xlwt
import io

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Foydalanuvchilar jadvali (user_name qo'shildi)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER UNIQUE,
        user_name TEXT,
        language TEXT DEFAULT 'uz'
    )
    """)

    # Tadbirlar jadvali (read_more_link qo'shildi)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        image_url TEXT,
        read_more_link TEXT,
        is_archived INTEGER DEFAULT 0
    )
    """)

    # Ro'yxatdan o'tganlar jadvali
    cur.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        event_id INTEGER,
        user_name TEXT,
        phone_number TEXT,
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id),
        FOREIGN KEY (event_id) REFERENCES events (id)
    )
    """)

    conn.commit()
    conn.close()

def add_user(user_id: int, user_name: str = None, lang: str = "uz"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO users (user_id, user_name, language) 
        VALUES (?, ?, COALESCE((SELECT language FROM users WHERE user_id = ?), ?))
    """, (user_id, user_name, user_id, lang))
    conn.commit()
    conn.close()

def set_user_language(user_id: int, lang: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET language=? WHERE user_id=?", (lang, user_id))
    conn.commit()
    conn.close()

def get_user_language(user_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else "uz"

def get_all_users() -> List[Tuple[int, str]]:
    """Get all users for admin messaging"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id, user_name FROM users")
    users = cur.fetchall()
    conn.close()
    return users

def add_event(title: str, description: str, image_url: str, read_more_link: str = None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO events (title, description, image_url, read_more_link) 
        VALUES (?, ?, ?, ?)
    """, (title, description, image_url, read_more_link))
    event_id = cur.lastrowid
    conn.commit()
    conn.close()
    return event_id

def get_events(active_only: bool = True) -> List[Tuple]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if active_only:
        cur.execute("SELECT id, title FROM events WHERE is_archived=0")
    else:
        cur.execute("SELECT id, title FROM events")
    events = cur.fetchall()
    conn.close()
    return events

def get_event_detail(event_id: int) -> Optional[Tuple]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT title, description, image_url, read_more_link FROM events WHERE id=?", (event_id,))
    event = cur.fetchone()
    conn.close()
    return event

def archive_event(event_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE events SET is_archived=1 WHERE id=?", (event_id,))
    conn.commit()
    conn.close()

def update_event(event_id: int, title: str, description: str, image_url: str, read_more_link: str = None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        UPDATE events SET title=?, description=?, image_url=?, read_more_link=? 
        WHERE id=?
    """, (title, description, image_url, read_more_link, event_id))
    conn.commit()
    conn.close()

def add_registration(user_id: int, event_id: int, user_name: str, phone_number: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO registrations (user_id, event_id, user_name, phone_number) 
        VALUES (?, ?, ?, ?)
    """, (user_id, event_id, user_name, phone_number))
    conn.commit()
    conn.close()

def is_user_registered(user_id: int, event_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM registrations WHERE user_id=? AND event_id=?", (user_id, event_id))
    result = cur.fetchone()
    conn.close()
    return result is not None

def get_event_registrations(event_id: int) -> List[Tuple]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT user_name, phone_number, registration_date 
        FROM registrations WHERE event_id=?
    """, (event_id,))
    registrations = cur.fetchall()
    conn.close()
    return registrations

def export_registrations_to_excel(event_id: int) -> io.BytesIO:
    """Export registrations to Excel file"""
    registrations = get_event_registrations(event_id)
    
    # Create workbook and worksheet
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('Registrations')
    
    # Headers
    headers = ['Name', 'Phone Number', 'Registration Date']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    
    # Data
    for row, (name, phone, date) in enumerate(registrations, 1):
        worksheet.write(row, 0, name or 'N/A')
        worksheet.write(row, 1, phone or 'N/A')
        worksheet.write(row, 2, date or 'N/A')
    
    # Save to BytesIO
    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)
    return output