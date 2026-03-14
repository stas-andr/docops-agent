from __future__ import annotations

import logging

from core.interfaces.agent_runtime import AgentRuntime
from core.interfaces.state_store import StateStore

logger = logging.getLogger(__name__)


class AgentService:
    def __init__(self, state_store: StateStore, runtime: AgentRuntime) -> None:
        self._state_store = state_store
        self._runtime = runtime

    def handle_query(self, user_id: str, query: str) -> str:
        normalized = query.strip()
        if not normalized:
            raise ValueError("Query must not be empty")

        logger.info("agent_request", extra={"user_id": user_id, "query": normalized})

        state = self._state_store.get(user_id)
        updated_state, answer = self._runtime.run(state=state, query=normalized)
        self._state_store.save(user_id, updated_state)
        return answer
