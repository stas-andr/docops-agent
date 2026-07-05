from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from api.dependencies import get_chat_model, get_retriever
from main import app
from repositories.markdown_retriever import MarkdownRetriever


class StubBoundModel:
    def invoke(self, messages: Sequence[BaseMessage]) -> AIMessage:
        last_human = next(
            message for message in reversed(messages) if isinstance(message, HumanMessage)
        )
        query = str(last_human.content)
        lower = query.lower()

        if lower.startswith("создай задачу:"):
            text = query.split(":", 1)[1].strip()
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "create_task",
                        "args": {"text": text},
                        "id": "call-create",
                        "type": "tool_call",
                    }
                ],
            )

        if "добавь комментарий:" in lower:
            comment = query.split(":", 1)[1].strip()
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "add_comment",
                        "args": {"comment": comment},
                        "id": "call-comment",
                        "type": "tool_call",
                    }
                ],
            )

        return AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "search_docs",
                    "args": {"query": query},
                    "id": "call-search",
                    "type": "tool_call",
                }
            ],
        )


class StubChatModel:
    def bind_tools(self, _: Sequence[Any]) -> StubBoundModel:
        return StubBoundModel()


def _make_client() -> TestClient:
    app.dependency_overrides[get_chat_model] = lambda: StubChatModel()
    app.dependency_overrides[get_retriever] = lambda: MarkdownRetriever(docs_dir="docs")
    return TestClient(app)


def test_health() -> None:
    client = _make_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rag_question() -> None:
    client = _make_client()
    response = client.post("/ask", json={"user_id": "u-rag", "query": "Что такое RAG?"})

    assert response.status_code == 200
    assert "RAG" in response.json()["answer"]


def test_create_task_and_add_comment_stateful() -> None:
    client = _make_client()

    create = client.post(
        "/ask",
        json={"user_id": "u-state", "query": "Создай задачу: добавить пример агента"},
    )
    assert create.status_code == 200
    assert "Задача создана" in create.json()["answer"]

    comment = client.post(
        "/ask",
        json={"user_id": "u-state", "query": "А теперь добавь комментарий: сделано"},
    )
    assert comment.status_code == 200
    assert "Комментарий добавлен" in comment.json()["answer"]


def test_add_comment_without_task() -> None:
    client = _make_client()

    response = client.post(
        "/ask",
        json={"user_id": "u-empty", "query": "А теперь добавь комментарий: сделано"},
    )

    assert response.status_code == 200
    assert "Нет активной задачи" in response.json()["answer"]
