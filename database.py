# =============================================
#   GRABZILLA BOT — database.py
#   Developer: @khojiakbar_khaydaraliyev
# =============================================

import sqlite3
from datetime import datetime


DB_PATH = "grabzilla.db"


def init_db():
    """Bazani yaratish"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            username    TEXT,
            full_name   TEXT,
            lang        TEXT DEFAULT 'uz',
            downloads   INTEGER DEFAULT 0,
            joined_at   TEXT,
            last_seen   TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS downloads (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            platform    TEXT,
            url         TEXT,
            quality     TEXT,
            downloaded_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def add_user(user_id: int, username: str, full_name: str):
    """Foydalanuvchi qo'shish yoki yangilash"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT OR IGNORE INTO users (user_id, username, full_name, joined_at, last_seen)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, username, full_name, now, now))
    c.execute("""
        UPDATE users SET username=?, full_name=?, last_seen=? WHERE user_id=?
    """, (username, full_name, now, user_id))
    conn.commit()
    conn.close()


def get_user_lang(user_id: int) -> str:
    """Foydalanuvchi tilini olish"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else "uz"


def set_user_lang(user_id: int, lang: str):
    """Foydalanuvchi tilini o'rnatish"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))
    conn.commit()
    conn.close()


def log_download(user_id: int, platform: str, url: str, quality: str = ""):
    """Yuklamani qayd etish"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO downloads (user_id, platform, url, quality, downloaded_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, platform, url, quality, now))
    c.execute("""
        UPDATE users SET downloads=downloads+1, last_seen=? WHERE user_id=?
    """, (now, user_id))
    conn.commit()
    conn.close()


def get_stats() -> dict:
    """Statistika olish"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM downloads")
    downloads = c.fetchone()[0]
    c.execute("SELECT last_seen FROM users ORDER BY last_seen DESC LIMIT 1")
    row = c.fetchone()
    last = row[0] if row else "—"
    conn.close()
    return {"users": users, "downloads": downloads, "last": last}
