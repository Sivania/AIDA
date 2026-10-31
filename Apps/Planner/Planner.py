from Apps.Planner.PlannerTools import PlannerTools
from Apps.Planner.PlannerRepository import PlannerRepository
from datetime import date, datetime, timedelta, timezone
class Planner:
    def __init__(self, database):
        self.conversation_repository = PlannerRepository(database)
        self.planner_tools = PlannerTools(self)
        
    def create_lane(self, name, description, position, priority, created_by):
        return self.conversation_repository.create_lane(name, description, position, priority, created_by)
    
    def update_lane(self, lane_id, updated_by, name=None, description=None, position=None, priority=None, status=None):
        return self.conversation_repository.update_lane(lane_id, updated_by, name, description, position, priority)
    
    def create_task(self, lane_id, title, description, status, created_by):
        return self.conversation_repository.create_task(lane_id, title, description, status, created_by)
    
    def update_task(self, task_id, updated_by, lane_id=None, title=None, description=None, status=None, labels=None, depends_on=None, due_date=None, done_date=None):
        return self.conversation_repository.update_task(task_id, updated_by, lane_id, title, description, status, labels, depends_on, due_date, done_date)

    def find_tasks(self, lane_id=None, status=None):
        return self.conversation_repository.find_tasks(lane_id, status)

    def get_task(self, task_id):
        return self.conversation_repository.get_task(task_id)

    def get_lanes(self, status=None):
        return self.conversation_repository.get_lanes(status)
    
    def tools(self):
        return self.planner_tools.tools()
    
    def get_app_context(self, due_within_days=7):
        today = datetime.now(timezone.utc).date()
        due_limit = (today + timedelta(days=due_within_days)).isoformat()
        query = self.conversation_repository.execute_query

        lanes = query("""
            SELECT id, name, priority, description
            FROM lanes
            WHERE status = 'active'
            ORDER BY position
        """)

        counts = query("""
            SELECT tasks.status, COUNT(*) AS count
            FROM tasks
            JOIN lanes ON lanes.id = tasks.lane_id
            WHERE lanes.status = 'active'
              AND tasks.status IN ('now', 'next', 'later', 'waiting')
            GROUP BY tasks.status
        """)

        current = query("""
            SELECT tasks.id, lanes.name AS lane, tasks.status, tasks.due_date, tasks.title
            FROM tasks
            JOIN lanes ON lanes.id = tasks.lane_id
            WHERE lanes.status = 'active'
              AND tasks.status IN ('now', 'next')
            ORDER BY tasks.status = 'next', tasks.due_date IS NULL, tasks.due_date, tasks.id
        """)

        due_soon = query("""
            SELECT tasks.id, lanes.name AS lane, tasks.status, tasks.due_date, tasks.title
            FROM tasks
            JOIN lanes ON lanes.id = tasks.lane_id
            WHERE lanes.status = 'active'
              AND tasks.status IN ('later', 'waiting')
              AND tasks.due_date IS NOT NULL
              AND tasks.due_date <= ?
            ORDER BY tasks.due_date, tasks.id
        """, (due_limit,))

        def task_line(task):
            due = ""
            if task["due_date"]:
                due_date = date.fromisoformat(task["due_date"])
                due = f" · due {due_date:%a} {due_date.day} {due_date:%b}"
                if due_date < today:
                    due += " (overdue)"
            return f"{task['id']} · {task['lane']} · {task['status']}{due} · {task['title']}"

        count_by_status = {row["status"]: row["count"] for row in counts}
        count_text = ", ".join(
            f"{count_by_status.get(status, 0)} {status}"
            for status in ("now", "next", "later", "waiting")
        )

        lines = [
            "Planner: Priority 1 is the most important lane.",
            "",
            "Lanes (id · name · priority · description):",
        ]
        lines += [f"{lane['id']} · {lane['name']} · {lane['priority']} · {lane['description'] or ''}" for lane in lanes] or ["None"]
        lines += ["", f"Open tasks: {count_text}.", "", "Now and next (id · lane · status · due · title):"]
        lines += [task_line(task) for task in current] or ["None"]
        lines += ["", f"Due within {due_within_days} days or overdue, not listed above:"]
        lines += [task_line(task) for task in due_soon] or ["None"]

        return "\n".join(lines)