import json
import sqlite3
from datetime import datetime, timezone

from langchain_core.tools import StructuredTool


class PlannerTools:
    def __init__(self, planner):
        self.planner = planner

    def planner_find_tasks(self, lane_id: int | None = None, status: str | None = None) -> str:
        """Find tasks in the planner. Deleted tasks are left out. Without a status, tasks with every status are returned.

        Args:
            lane_id: Only tasks in this lane.
            status: Only tasks with this status: now, next, later, waiting or done.
        """
        tasks = self.planner.find_tasks(lane_id=lane_id, status=status)
        if not tasks:
            return "No tasks found."
        return "\n".join(f"{t['id']} · lane {t['lane_id']} · {t['status']} · {t['title']}" for t in tasks)

    def planner_get_task(self, task_id: int) -> str:
        """Get one task with all its details: description, labels, dependencies and dates.

        Args:
            task_id: The id of the task.
        """
        task = self.planner.get_task(task_id)
        if task is None:
            return f"No task with id {task_id}."
        labels = json.loads(task["labels"])
        depends_on = json.loads(task["depends_on"])
        return "\n".join([
            f"{task['id']} · {task['title']}",
            f"Lane: {task['lane_id']} · Status: {task['status']}",
            f"Due: {task['due_date'] or 'none'} · Done: {task['done_date'] or 'not done'}",
            f"Labels: {', '.join(labels) or 'none'}",
            f"Depends on: {', '.join(str(i) for i in depends_on) or 'nothing'}",
            f"Description: {task['description'] or 'none'}",
        ])

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

    def planner_update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        lane_id: int | None = None,
        due_date: str | None = None,
        labels: list[str] | None = None,
        depends_on: list[int] | None = None,
    ) -> str:
        """Change a task. Only the fields you give are changed.

        Args:
            task_id: The id of the task.
            title: New title.
            description: New description.
            status: now, next, later or waiting. Use planner_complete_task to finish a task.
            lane_id: Move the task to this lane.
            due_date: New due date as YYYY-MM-DD.
            labels: The full new list of labels.
            depends_on: The full new list of ids of tasks that must be done first.
        """
        if self.planner.get_task(task_id) is None:
            return f"No task with id {task_id}."
        if status in ("done", "deleted"):
            return "Not saved: status can only be now, next, later or waiting here. Use planner_complete_task to finish a task."
        try:
            self.planner.update_task(
                task_id,
                "aida",
                title=title,
                description=description,
                status=status,
                lane_id=lane_id,
                due_date=due_date,
                labels=json.dumps(labels) if labels is not None else None,
                depends_on=json.dumps(depends_on) if depends_on is not None else None,
            )
        except sqlite3.IntegrityError as error:
            return f"Not saved: {error}"
        return f"Updated task {task_id}."

    def planner_complete_task(self, task_id: int) -> str:
        """Mark a task as done, with today's date.

        Args:
            task_id: The id of the task.
        """
        if self.planner.get_task(task_id) is None:
            return f"No task with id {task_id}."
        today = datetime.now(timezone.utc).date().isoformat()
        self.planner.update_task(task_id, "aida", status="done", done_date=today)
        return f"Task {task_id} is done ({today})."

    def planner_create_lane(self, name: str, position: int, priority: int, description: str = "") -> str:
        """Create a lane: an area of their life or work that tasks belong to.

        Args:
            name: The lane's name. Must be unique.
            position: Where the lane is shown. 1 is first.
            priority: How important the lane is. 1 is the most important.
            description: A short summary of what the lane is about.
        """
        try:
            lane_id = self.planner.create_lane(name, description, position, priority, "aida")
        except sqlite3.IntegrityError as error:
            return f"Not saved: {error}"
        return f"Created lane {lane_id}: {name}"

    def tools(self):
        return [
            StructuredTool.from_function(self.planner_find_tasks, parse_docstring=True),
            StructuredTool.from_function(self.planner_get_task, parse_docstring=True),
            StructuredTool.from_function(self.planner_create_task, parse_docstring=True),
            StructuredTool.from_function(self.planner_update_task, parse_docstring=True),
            StructuredTool.from_function(self.planner_complete_task, parse_docstring=True),
            StructuredTool.from_function(self.planner_create_lane, parse_docstring=True),
        ]