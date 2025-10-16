import json

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Space(Base):
    __tablename__ = "spaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    artifacts = relationship(
        "Artifact", back_populates="space", cascade="all, delete-orphan"
    )
    agents = relationship(
        "Agent", back_populates="space", cascade="all, delete-orphan"
    )
    interactions = relationship(
        "Interaction", back_populates="space", cascade="all, delete-orphan"
    )


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey("spaces.id"), nullable=False)
    title = Column(String(150), nullable=False)
    content = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=True)
    file_path = Column(String(255), nullable=True)
    mime_type = Column(String(100), nullable=True)
    summary = Column(Text, nullable=True)
    _tags = Column("tags", Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    space = relationship("Space", back_populates="artifacts")

    @property
    def tags(self) -> list[str]:
        if not self._tags:
            return []
        try:
            return json.loads(self._tags)
        except (json.JSONDecodeError, TypeError):
            return []

    @tags.setter
    def tags(self, value: list[str] | str | None) -> None:
        if value is None:
            self._tags = None
        elif isinstance(value, str):
            self._tags = value
        else:
            self._tags = json.dumps(list(value))


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey("spaces.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    model = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False, default="echo")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    space = relationship("Space", back_populates="agents")
    interactions = relationship(
        "Interaction", back_populates="agent", cascade="all, delete-orphan"
    )


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    space_id = Column(Integer, ForeignKey("spaces.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=True)
    response = Column(Text, nullable=False)
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    context_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    agent = relationship("Agent", back_populates="interactions")
    space = relationship("Space", back_populates="interactions")

    @property
    def context(self) -> list[dict]:
        if not self.context_json:
            return []
        try:
            return json.loads(self.context_json)
        except (json.JSONDecodeError, TypeError):
            return []

    @context.setter
    def context(self, value: list[dict] | None) -> None:
        if value is None:
            self.context_json = None
        else:
            self.context_json = json.dumps(value)
