from __future__ import annotations

from typing import Protocol


class TaskTracker(Protocol):
    def create_task(self, text: str) -> str:
        ...

    def add_comment(self, task_id: str, comment: str) -> None:
        ...
