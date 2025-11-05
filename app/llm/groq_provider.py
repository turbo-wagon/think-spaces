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


class GroqProviderError(RuntimeError):
    pass


@dataclass
class GroqProvider(LLMProvider):
    """LLM provider that calls Groq's API (OpenAI-compatible).

    Groq provides extremely fast inference for open-source models like:
    - llama-3.1-70b-versatile
    - llama-3.1-8b-instant
    - mixtral-8x7b-32768
    - gemma2-9b-it

    Get your API key at: https://console.groq.com
    """

    name: str = "groq"
    model: str = "llama-3.1-70b-versatile"
    api_key: Optional[str] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if AsyncOpenAI is None:
            raise GroqProviderError(
                "openai package is not installed; install dependencies to use this provider"
            )

        if not self.api_key:
            self.api_key = os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise GroqProviderError(
                "GROQ_API_KEY is not set; configure it to enable the Groq provider. "
                "Get your key at https://console.groq.com"
            )

        self._client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )

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
            "provider": "groq",
            "usage": completion.usage.model_dump() if completion.usage else {},
        }

        return CompletionResponse(output=output, metadata=metadata)


registry.register(GroqProvider)
