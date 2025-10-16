from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ArtifactBase(BaseModel):
    title: str = Field(..., max_length=150)
    content: Optional[str] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None


class ArtifactCreate(ArtifactBase):
    space_id: int
    file_path: Optional[str] = None


class ArtifactUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=150)
    content: Optional[str] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_path: Optional[str] = None


class ArtifactRead(ArtifactBase):
    id: int
    space_id: int
    created_at: datetime
    file_path: Optional[str] = None
    summary: Optional[str] = None
    tags: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SpaceBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None


class SpaceCreate(SpaceBase):
    pass


class SpaceUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class SpaceRead(SpaceBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SpaceDetail(SpaceRead):
    artifacts: list[ArtifactRead] = []
    agents: list["AgentRead"] = []


class AgentBase(BaseModel):
    name: str = Field(..., max_length=100)
    model: str = Field(..., max_length=100)
    description: Optional[str] = None
    provider: str = Field(default="echo", max_length=50)
    system_prompt: Optional[str] = None


class AgentCreate(AgentBase):
    space_id: int


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    provider: Optional[str] = Field(None, max_length=50)
    system_prompt: Optional[str] = None


class AgentRead(AgentBase):
    id: int
    space_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


SpaceDetail.model_rebuild()


class AgentInteractionRequest(BaseModel):
    prompt: str
    system: Optional[str] = None
    context_limit: int = Field(default=5, ge=0, le=25)


class AgentInteractionResponse(BaseModel):
    output: str
    provider: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    context: list[dict[str, Any]] = Field(default_factory=list)


class InteractionRead(BaseModel):
    id: int
    agent_id: int
    space_id: int
    prompt: str
    system_prompt: Optional[str] = None
    response: str
    provider: str
    model: str
    context: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
