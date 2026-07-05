from __future__ import annotations

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=128)
    query: str = Field(min_length=1, max_length=2000)


class AskResponse(BaseModel):
    answer: str
