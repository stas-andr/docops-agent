from __future__ import annotations

import json

from langchain_core.tools import BaseTool, tool

from core.interfaces.task_tracker import TaskTracker


def create_create_task_tool(task_tracker: TaskTracker) -> BaseTool:
    @tool
    def create_task(text: str) -> str:
        """Create a task or ticket and return its identifier."""
        normalized = text.strip()
        if not normalized:
            raise ValueError("Task text must not be empty")

        task_id = task_tracker.create_task(normalized)
        return json.dumps(
            {
                "answer": f"Задача создана: {task_id}",
                "last_topic": "create_task",
                "task_id": task_id,
            },
            ensure_ascii=False,
        )

    return create_task


def create_add_comment_tool(task_tracker: TaskTracker) -> BaseTool:
    @tool
    def add_comment(comment: str, task_id: str | None = None) -> str:
        """Add a comment to an existing task. Use the active task when task_id is omitted."""
        normalized = comment.strip()
        if not normalized:
            raise ValueError("Comment must not be empty")
        if not task_id:
            return json.dumps(
                {
                    "answer": "Нет активной задачи для комментария. Сначала создайте задачу.",
                    "last_topic": "add_comment",
                    "task_id": None,
                },
                ensure_ascii=False,
            )

        task_tracker.add_comment(task_id, normalized)
        return json.dumps(
            {
                "answer": f"Комментарий добавлен к {task_id}",
                "last_topic": "add_comment",
                "task_id": task_id,
            },
            ensure_ascii=False,
        )

    return add_comment
