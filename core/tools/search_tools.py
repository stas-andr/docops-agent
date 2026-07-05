from __future__ import annotations

import json

from langchain_core.tools import BaseTool, tool

from core.interfaces.retriever import Retriever


def create_search_docs_tool(retriever: Retriever) -> BaseTool:
    @tool
    def search_docs(query: str) -> str:
        """Find relevant internal documentation and return the final answer."""
        normalized = query.strip()
        if not normalized:
            raise ValueError("Query must not be empty")

        contexts = retriever.retrieve(normalized, top_k=2)
        if not contexts:
            answer = "Информация по этому запросу в документации не найдена."
        else:
            joined_contexts = "\n\n".join(contexts)
            answer = f"Ответ по документации:\n{joined_contexts}"

        return json.dumps(
            {"answer": answer, "last_topic": "search_docs", "task_id": None},
            ensure_ascii=False,
        )

    return search_docs
