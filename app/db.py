import sqlite3
import os
from datetime import datetime

def ensure_data_dir(data_dir):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)

def configure_sqlite(conn):
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")

def get_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    configure_sqlite(conn)
    return conn

def init_db(db_path):
    ensure_data_dir(os.path.dirname(db_path))
    conn = get_connection(db_path)
    
    # Tabla items
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            qty INTEGER DEFAULT 1,
            category TEXT,
            done INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabla categories
    conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            name TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Seed categories
    default_categories = ["Sin categoría", "Frutas y Verduras", "Lácteos", "Limpieza"]
    for category in default_categories:
        conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
    
    conn.commit()
    conn.close()
