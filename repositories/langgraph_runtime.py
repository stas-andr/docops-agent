from __future__ import annotations

import json
import logging
from typing import Any, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph

from core.interfaces.agent_runtime import AgentRuntime
from core.state import State

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Ты — агент компании TSI. Ты можешь выполнять два типа задач:\n"
    "1. Отвечать на вопросы по внутренней документации — используй инструмент search_docs.\n"
    "2. Управлять задачами — используй create_task или add_comment, если пользователь просит "
    "создать задачу, тикет или добавить комментарий.\n"
    "\n"
    "Правила:\n"
    "- НИКОГДА не выдумывай информацию.\n"
    "- Если вопрос о документации, но контекст не найден — скажи: "
    "'Информация по этому запросу в документации не найдена.'\n"
    "- Если запрос — создать задачу или добавить комментарий, "
    "вызывай соответствующий инструмент.\n"
    "- НЕ используй search_docs для запросов вроде 'создай', 'добавь', 'зарегистрируй'."
)


class LangGraphRuntime(AgentRuntime):
    def __init__(self, model: Any, tools: list[BaseTool]) -> None:
        self._model = model
        self._tools = tools
        self._tools_by_name = {tool.name: tool for tool in tools}
        workflow = StateGraph(State)
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", self.tool_node)
        workflow.add_node("update", self.update_state)
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            self.route_after_agent,
            {"tools": "tools", END: END},
        )
        workflow.add_edge("tools", "update")
        workflow.add_conditional_edges("update", self.route_after_update, {END: END})
        self._graph = workflow.compile()

    def run(self, state: State, query: str) -> tuple[State, str]:
        input_state: State = {
            "messages": [*state["messages"], HumanMessage(content=query)],
            "last_topic": state["last_topic"],
            "task_id": state["task_id"],
        }
        result = cast(State, self._graph.invoke(cast(Any, input_state)))
        return result, self._extract_answer(result["messages"])

    def call_model(self, state: State) -> dict[str, list[BaseMessage]]:
        messages: list[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        if state["task_id"]:
            messages.insert(
                1,
                SystemMessage(
                    content=f"Текущая активная задача пользователя: {state['task_id']}. "
                    "Если пользователь просит добавить комментарий, используй этот task_id.",
                ),
            )

        response = self._model.bind_tools(self._tools).invoke(messages)
        logger.info(
            "model_turn_completed",
            extra={"has_tool_calls": bool(getattr(response, "tool_calls", []))},
        )
        return {"messages": [response]}

    def tool_node(self, state: State) -> dict[str, list[ToolMessage]]:
        last_message = state["messages"][-1]
        if not isinstance(last_message, AIMessage):
            return {"messages": []}

        tool_messages: list[ToolMessage] = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool = self._tools_by_name[tool_name]
            tool_args = dict(tool_call.get("args", {}))
            if tool_name == "add_comment" and not tool_args.get("task_id"):
                tool_args["task_id"] = state["task_id"]

            tool_result = tool.invoke(tool_args)
            tool_messages.append(
                ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call["id"],
                    name=tool_name,
                )
            )
        return {"messages": tool_messages}

    def update_state(self, state: State) -> dict[str, Any]:
        last_message = state["messages"][-1]
        if not isinstance(last_message, ToolMessage):
            return {}

        if not isinstance(last_message.content, str):
            raise ValueError("Tool message content must be a JSON string")

        payload = json.loads(last_message.content)
        answer = payload["answer"]
        next_task_id = payload["task_id"] if payload["task_id"] is not None else state["task_id"]
        if payload["last_topic"] == "add_comment" and payload["task_id"] is None:
            next_task_id = state["task_id"]

        return {
            "messages": [AIMessage(content=answer)],
            "last_topic": payload["last_topic"],
            "task_id": next_task_id,
        }

    @staticmethod
    def route_after_agent(state: State) -> str:
        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tools"
        return END

    @staticmethod
    def route_after_update(_: State) -> str:
        return END

    @staticmethod
    def _extract_answer(messages: list[BaseMessage]) -> str:
        for message in reversed(messages):
            if isinstance(message, AIMessage) and isinstance(message.content, str):
                return message.content
        return "Не удалось сформировать ответ."
