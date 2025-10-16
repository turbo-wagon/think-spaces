from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Optional


@dataclass(slots=True)
class CompletionRequest:
    prompt: str
    system: Optional[str] = None
    context: Iterable[str] = field(default_factory=tuple)
    options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CompletionResponse:
    output: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


class LLMProvider(ABC):
    """Interface all LLM providers must implement."""

    name: str

    @abstractmethod
    async def generate(self, request: CompletionRequest) -> CompletionResponse:
        """Produce a completion for the given request."""

