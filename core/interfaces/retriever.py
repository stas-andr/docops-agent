from __future__ import annotations

from typing import Protocol


class Retriever(Protocol):
    def retrieve(self, query: str, top_k: int = 2) -> list[str]:
        ...
