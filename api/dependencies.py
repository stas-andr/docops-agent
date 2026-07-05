from __future__ import annotations

import os
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from langchain_ollama import ChatOllama, OllamaEmbeddings

from core.agent_service import AgentService
from core.interfaces.agent_runtime import AgentRuntime
from core.interfaces.retriever import Retriever
from core.interfaces.state_store import StateStore
from core.interfaces.task_tracker import TaskTracker
from core.tools import create_add_comment_tool, create_create_task_tool, create_search_docs_tool
from repositories.chroma_retriever import ChromaRetriever
from repositories.in_memory_state import InMemoryStateStore
from repositories.in_memory_tasks import InMemoryTaskTracker
from repositories.langgraph_runtime import LangGraphRuntime

_state_store = InMemoryStateStore()
_task_tracker = InMemoryTaskTracker()


def get_state_store() -> StateStore:
    return _state_store


def get_task_tracker() -> TaskTracker:
    return _task_tracker


@lru_cache(maxsize=1)
def _build_retriever() -> Retriever:
    embeddings = OllamaEmbeddings(model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"))
    return ChromaRetriever(embeddings=embeddings, docs_dir="docs")


def get_retriever() -> Retriever:
    return _build_retriever()


@lru_cache(maxsize=1)
def get_chat_model() -> ChatOllama:
    return ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3.2"), temperature=0)


def get_agent_runtime(
    task_tracker: Annotated[TaskTracker, Depends(get_task_tracker)],
    retriever: Annotated[Retriever, Depends(get_retriever)],
    chat_model: Annotated[ChatOllama, Depends(get_chat_model)],
) -> AgentRuntime:
    tools = [
        create_search_docs_tool(retriever),
        create_create_task_tool(task_tracker),
        create_add_comment_tool(task_tracker),
    ]
    return LangGraphRuntime(model=chat_model, tools=tools)


def get_agent_service(
    state_store: Annotated[StateStore, Depends(get_state_store)],
    runtime: Annotated[AgentRuntime, Depends(get_agent_runtime)],
) -> AgentService:
    return AgentService(state_store=state_store, runtime=runtime)
