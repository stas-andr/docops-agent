from __future__ import annotations

from core.state import State


class InMemoryStateStore:
    def __init__(self, messages_limit: int = 50) -> None:
        self._states: dict[str, State] = {}
        self._messages_limit = messages_limit

    def get(self, user_id: str) -> State:
        state = self._states.get(user_id)
        if state is None:
            state = {"messages": [], "last_topic": None, "task_id": None}
            self._states[user_id] = state
        return {
            "messages": list(state["messages"]),
            "last_topic": state["last_topic"],
            "task_id": state["task_id"],
        }

    def save(self, user_id: str, state: State) -> None:
        messages = state["messages"]
        if len(messages) > self._messages_limit:
            messages = messages[-self._messages_limit :]

        self._states[user_id] = {
            "messages": list(messages),
            "last_topic": state["last_topic"],
            "task_id": state["task_id"],
        }
