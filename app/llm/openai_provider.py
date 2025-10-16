from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

from .registry import registry
from .types import CompletionRequest, CompletionResponse, LLMProvider

try:
    from openai import AsyncOpenAI
except ImportError:  # pragma: no cover - handled at runtime
    AsyncOpenAI = None  # type: ignore


class OpenAIProviderError(RuntimeError):
    pass


@dataclass
class OpenAIProvider(LLMProvider):
    """LLM provider that calls OpenAI's chat completions API."""

    name: str = "openai"
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if AsyncOpenAI is None:
            raise OpenAIProviderError(
                "openai package is not installed; install dependencies to use this provider"
            )

        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise OpenAIProviderError(
                "OPENAI_API_KEY is not set; configure it to enable the OpenAI provider"
            )

        self._client = AsyncOpenAI(api_key=self.api_key)

    async def generate(self, request: CompletionRequest) -> CompletionResponse:
        model_name = request.options.get("model") if request.options else None
        model = model_name or self.model

        messages = []
        if request.system:
            messages.append({"role": "system", "content": request.system})

        if request.context:
            context_text = "\n".join(request.context)
            messages.append({"role": "system", "content": f"Context:\n{context_text}"})

        messages.append({"role": "user", "content": request.prompt})

        completion = await self._client.chat.completions.create(
            model=model,
            messages=messages,
        )

        choice = completion.choices[0]
        output = choice.message.content or ""

        metadata = {
            "model": completion.model,
            "usage": completion.usage.model_dump() if completion.usage else {},
        }

        return CompletionResponse(output=output, metadata=metadata)


registry.register(OpenAIProvider)
