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
                    type TEXT,
                    runs_completed INTEGER DEFAULT 0,
                    cafe_visits INTEGER DEFAULT 0,
                    energy_left REAL DEFAULT 100
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    visitor_id INTEGER,
                    event_type TEXT,
                    area TEXT,
                    wait_time REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()

    def save_visitor(self, visitor):
        with self.lock:
            self.cursor.execute("""
                INSERT OR IGNORE INTO visitors (id, type)
                VALUES (?, ?)
            """, (visitor.visitor_id, visitor.visitor_type))
            self.conn.commit()

    def update_visitor_summary(self, visitor):
        with self.lock:
            self.cursor.execute("""
                UPDATE visitors
                SET runs_completed = ?, cafe_visits = ?, energy_left = ?
                WHERE id = ?
            """, (
                visitor.runs_completed,
                visitor.cafe_visits,
                visitor.energy,
                visitor.visitor_id
            ))
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