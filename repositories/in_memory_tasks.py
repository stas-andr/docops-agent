from __future__ import annotations

from collections.abc import Iterable
from uuid import uuid4


class InMemoryTaskTracker:
    def __init__(self) -> None:
        self.tasks: dict[str, str] = {}
        self.comments: dict[str, list[str]] = {}

    def create_task(self, text: str) -> str:
        task_id = f"task-{uuid4().hex[:8]}"
        self.tasks[task_id] = text
        self.comments[task_id] = []
        return task_id

    def add_comment(self, task_id: str, comment: str) -> None:
        if task_id not in self.tasks:
            raise KeyError(f"Task not found: {task_id}")
        self.comments[task_id].append(comment)

    def get_comments(self, task_id: str) -> Iterable[str]:
        return tuple(self.comments.get(task_id, ()))
