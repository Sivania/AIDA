class PlannerRepository:
    def __init__(self, database):
        self.database = database
        self._initialize_tables()
 
    def _initialize_tables(self):
        self.database.execute_write("""
            CREATE TABLE IF NOT EXISTS lanes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                position INTEGER NOT NULL,
                priority INTEGER NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('active', 'closed', 'deleted')),
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                updated_by TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
            )
        """)

        self.database.execute_write("""
            CREATE TABLE IF NOT EXISTS lanes_rev (
                rev_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT NOT NULL,
                id INTEGER NOT NULL,
                name TEXT,
                description TEXT,
                position INTEGER,
                priority INTEGER,
                status TEXT,
                created_by TEXT,
                created_at TEXT,
                updated_by TEXT,
                updated_at TEXT
            )
        """)
 
        self.database.execute_write("""
            CREATE TRIGGER IF NOT EXISTS lanes_after_insert
            AFTER INSERT ON lanes
            BEGIN
                INSERT INTO lanes_rev (event, id, name, description, position, priority, status, created_by, created_at, updated_by, updated_at)
                VALUES ('inserted', NEW.id, NEW.name, NEW.description, NEW.position, NEW.priority, NEW.status, NEW.created_by, NEW.created_at, NEW.updated_by, NEW.updated_at);
            END
        """)
 
        self.database.execute_write("""
            CREATE TRIGGER IF NOT EXISTS lanes_after_update
            AFTER UPDATE ON lanes
            BEGIN
                INSERT INTO lanes_rev (event, id, name, description, position, priority, status, created_by, created_at, updated_by, updated_at)
                VALUES ('updated', NEW.id, NEW.name, NEW.description, NEW.position, NEW.priority, NEW.status, NEW.created_by, NEW.created_at, NEW.updated_by, NEW.updated_at);
            END
        """)
 
        self.database.execute_write("""
            CREATE TRIGGER IF NOT EXISTS lanes_no_delete
            BEFORE DELETE ON lanes
            BEGIN
                SELECT RAISE(ABORT, 'lanes are never deleted, set status to deleted');
            END
        """)
        
        
        
        self.database.execute_write("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lane_id INTEGER NOT NULL REFERENCES lanes (id),
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL CHECK (status IN ('now', 'next', 'later', 'waiting', 'done', 'deleted')),
                labels TEXT NOT NULL DEFAULT '[]',
                depends_on TEXT NOT NULL DEFAULT '[]',
                due_date TEXT,
                done_date TEXT,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                updated_by TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
            )
        """)

        self.database.execute_write("""
            CREATE TABLE IF NOT EXISTS tasks_rev (
                rev_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT NOT NULL,
                id INTEGER NOT NULL,
                lane_id INTEGER,
                title TEXT,
                description TEXT,
                status TEXT,
                labels TEXT,
                depends_on TEXT,
                due_date TEXT,
                done_date TEXT,
                created_by TEXT,
                created_at TEXT,
                updated_by TEXT,
                updated_at TEXT
            )
        """)
        
        self.database.execute_write("""
            CREATE TRIGGER IF NOT EXISTS tasks_after_insert
            AFTER INSERT ON tasks
            BEGIN
                INSERT INTO tasks_rev (event, id, lane_id, title, description, status, labels, depends_on, due_date, done_date, created_by, created_at, updated_by, updated_at)
                VALUES ('inserted', NEW.id, NEW.lane_id, NEW.title, NEW.description, NEW.status, NEW.labels, NEW.depends_on, NEW.due_date, NEW.done_date, NEW.created_by, NEW.created_at, NEW.updated_by, NEW.updated_at);
            END
        """)

        self.database.execute_write("""
            CREATE TRIGGER IF NOT EXISTS tasks_after_update
            AFTER UPDATE ON tasks
            BEGIN
                INSERT INTO tasks_rev (event, id, lane_id, title, description, status, labels, depends_on, due_date, done_date, created_by, created_at, updated_by, updated_at)
                VALUES ('updated', NEW.id, NEW.lane_id, NEW.title, NEW.description, NEW.status, NEW.labels, NEW.depends_on, NEW.due_date, NEW.done_date, NEW.created_by, NEW.created_at, NEW.updated_by, NEW.updated_at);
            END
        """)

        self.database.execute_write("""
            CREATE TRIGGER IF NOT EXISTS tasks_no_delete
            BEFORE DELETE ON tasks
            BEGIN
                SELECT RAISE(ABORT, 'tasks are never deleted, set status to deleted');
            END
        """)
                    
    def create_lane(self, name: str, description: str, position: int, priority: int, created_by: str):
        return self.database.execute_write("""
            INSERT INTO lanes (name, description, position, priority, status, created_by, updated_by)
            VALUES (?, ?, ?, ?, 'active', ?, ?)
        """, (name, description, position, priority, created_by, created_by))
        
    def create_task(self, lane_id: int, title: str, description: str, status: str, created_by: str, due_date: str = None, done_date: str = None, labels: str = '[]', depends_on: str = '[]'):
        return self.database.execute_write("""
            INSERT INTO tasks (lane_id, title, description, status, created_by, updated_by, due_date, done_date, labels, depends_on)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (lane_id, title, description, status, created_by, created_by, due_date, done_date, labels, depends_on))

    def update_lane(self, lane_id, updated_by, name=None, description=None, position=None, priority=None):
        changes = {"name": name, "description": description, "position": position, "priority": priority}
        changes = {column: value for column, value in changes.items() if value is not None}
        if not changes:
            return
        set_clause = ", ".join(f"{column} = ?" for column in changes)
        self.database.execute_write(f"""
            UPDATE lanes
            SET {set_clause}, updated_by = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            WHERE id = ?
        """, (*changes.values(), updated_by, lane_id))


                
    def update_task(self, task_id, updated_by,lane_id=None, title=None, description=None, status=None, labels=None, depends_on=None, due_date=None, done_date=None):
        changes = {
            "lane_id": lane_id,
            "title": title,
            "description": description,
            "status": status,
            "labels": labels,
            "depends_on": depends_on,
            "due_date": due_date,
            "done_date": done_date
        }
        changes = {column: value for column, value in changes.items() if value is not None}
        if not changes:
            return
        set_clause = ", ".join(f"{column} = ?" for column in changes)
        self.database.execute_write(f"""
            UPDATE tasks
             SET {set_clause}, updated_by = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            WHERE id = ?
        """, (*changes.values(), updated_by, task_id))

    def set_lane_status(self, lane_id, status, updated_by):
        self.database.execute_write("""
            UPDATE lanes
            SET status = ?, updated_by = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            WHERE id = ?
        """, (status, updated_by, lane_id))