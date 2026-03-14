from __future__ import annotations

from typing import Protocol

from core.state import State


class StateStore(Protocol):
    def get(self, user_id: str) -> State:
        ...

    def save(self, user_id: str, state: State) -> None:
        ...
