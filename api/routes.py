from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import get_agent_service
from core.agent_service import AgentService
from schemas.chat import AskRequest, AskResponse

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/ask", response_model=AskResponse)
def ask(
    payload: AskRequest,
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
) -> AskResponse:
    answer = agent_service.handle_query(user_id=payload.user_id, query=payload.query)
    return AskResponse(answer=answer)
