import sqlite3
import threading


class DatabaseManager:
    def __init__(self, db_name="resort.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()


    def create_tables(self):
        with self.lock:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS visitors (
                    id INTEGER PRIMARY KEY,
                    type TEXT
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    visitor_id INTEGER,
                    event_type TEXT,
                    area TEXT,
                    wait_time REAL
                )
            """)

            self.conn.commit()


    def save_visitor(self, visitor):
        with self.lock:
            self.cursor.execute("""
                INSERT INTO visitors (id, type)
                VALUES (?, ?)
            """, (visitor.id, visitor.type))

            self.conn.commit()


    def log_event(self, visitor_id, event_type, area, wait_time):
        with self.lock:
            self.cursor.execute("""
                INSERT INTO events (visitor_id, event_type, area, wait_time)
                VALUES (?, ?, ?, ?)
            """, (visitor_id, event_type, area, wait_time))

            self.conn.commit()


    def close(self):
        self.conn.close()