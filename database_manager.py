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
                    age_group TEXT,
                    skill_level TEXT,
                    own_equipment INTEGER DEFAULT 0,
                    ski_school INTEGER DEFAULT 0,
                    injury_status TEXT DEFAULT 'none',
                    runs_completed INTEGER DEFAULT 0,
                    cafe_visits INTEGER DEFAULT 0,
                    restaurant_visits INTEGER DEFAULT 0,
                    apres_ski_visits INTEGER DEFAULT 0,
                    first_aid_visits INTEGER DEFAULT 0,
                    instructor_visits INTEGER DEFAULT 0,
                    equipment_returns INTEGER DEFAULT 0,
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
                    severity TEXT,
                    weather TEXT,
                    age_group TEXT,
                    skill_level TEXT,
                    own_equipment INTEGER,
                    ski_school INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()

    def save_visitor(self, visitor):
        with self.lock:
            self.cursor.execute("""
                INSERT OR IGNORE INTO visitors (
                    id,
                    type,
                    age_group,
                    skill_level,
                    own_equipment,
                    ski_school,
                    injury_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                visitor.visitor_id,
                visitor.visitor_type,
                getattr(visitor, "age_group", None),
                getattr(visitor, "skill_level", None),
                int(getattr(visitor, "has_own_equipment", False)),
                int(getattr(visitor, "is_ski_school", False)),
                getattr(visitor, "injury_status", "none"),
            ))
            self.conn.commit()

    def update_visitor_summary(self, visitor):
        with self.lock:
            self.cursor.execute("""
                UPDATE visitors
                SET runs_completed = ?,
                    cafe_visits = ?,
                    restaurant_visits = ?,
                    apres_ski_visits = ?,
                    first_aid_visits = ?,
                    instructor_visits = ?,
                    equipment_returns = ?,
                    injury_status = ?,
                    energy_left = ?
                WHERE id = ?
            """, (
                getattr(visitor, "runs_completed", 0),
                getattr(visitor, "cafe_visits", 0),
                getattr(visitor, "restaurant_visits", 0),
                getattr(visitor, "apres_ski_visits", 0),
                getattr(visitor, "first_aid_visits", 0),
                getattr(visitor, "instructor_visits", 0),
                getattr(visitor, "equipment_returns", 0),
                getattr(visitor, "injury_status", "none"),
                getattr(visitor, "energy", 100),
                visitor.visitor_id
            ))
            self.conn.commit()

    def log_event(
        self,
        visitor_id,
        event_type,
        area,
        wait_time,
        severity=None,
        weather=None,
        age_group=None,
        skill_level=None,
        own_equipment=False,
        ski_school=False
    ):
        with self.lock:
            self.cursor.execute("""
                INSERT INTO events (
                    visitor_id,
                    event_type,
                    area,
                    wait_time,
                    severity,
                    weather,
                    age_group,
                    skill_level,
                    own_equipment,
                    ski_school
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                visitor_id,
                event_type,
                area,
                wait_time,
                severity,
                weather,
                age_group,
                skill_level,
                int(own_equipment),
                int(ski_school),
            ))
            self.conn.commit()

    def close(self):
        self.conn.close()