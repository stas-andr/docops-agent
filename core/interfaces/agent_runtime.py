from __future__ import annotations

from typing import Protocol

from core.state import State


class AgentRuntime(Protocol):
    def run(self, state: State, query: str) -> tuple[State, str]:
        ...
