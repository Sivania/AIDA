import sqlite3
from langchain_core.tools import StructuredTool


class PlannerTools:
    def __init__(self, planner):
        self.planner = planner

    def planner_find_tasks(self, lane_id: int | None = None, status: str | None = None) -> str:
        """Find tasks in the planner. Deleted tasks are left out.

        Args:
            lane_id: Only tasks in this lane.
            status: Only tasks with this status: now, next, later, waiting or done.
        """
        tasks = self.planner.find_tasks(lane_id=lane_id, status=status)
        if not tasks:
            return "No tasks found."
        return "\n".join(f"{t['id']} · lane {t['lane_id']} · {t['status']} · {t['title']}" for t in tasks)

    def planner_create_task(self, lane_id: int, title: str, description: str = "", status: str = "now") -> str:
        """Create a task in a lane.

        Args:
            lane_id: The lane the task belongs to.
            title: What needs to be done, in a few words.
            description: More detail, if any.
            status: now, next, later or waiting.
        """
        try:
            task_id = self.planner.create_task(lane_id, title, description, status, "aida")
        except sqlite3.IntegrityError as error:
            return f"Not saved: {error}"
        return f"Created task {task_id}: {title}"

    def tools(self):
        return [
            StructuredTool.from_function(self.planner_find_tasks, parse_docstring=True),
            StructuredTool.from_function(self.planner_create_task, parse_docstring=True),
        ]