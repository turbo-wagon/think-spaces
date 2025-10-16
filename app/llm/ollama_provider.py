from __future__ import annotations

import os
from dataclasses import dataclass, field

import httpx

from .registry import registry
from .types import CompletionRequest, CompletionResponse, LLMProvider


class OllamaProviderError(RuntimeError):
    pass


@dataclass
class OllamaProvider(LLMProvider):
    """LLM provider that talks to a local Ollama instance."""

    name: str = "ollama"
    model: str = "llama3"
    base_url: str = field(
        default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )

    async def generate(self, request: CompletionRequest) -> CompletionResponse:
        target_model = request.options.get("model") if request.options else None
        model = target_model or self.model

        prompt_parts = []
        if request.system:
            prompt_parts.append(f"System:\n{request.system}")
        if request.context:
            prompt_parts.append("Context:\n" + "\n".join(request.context))
        prompt_parts.append(request.prompt)
        prompt = "\n\n".join(prompt_parts)

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=30) as client:
                response = await client.post("/api/generate", json=payload)
        except httpx.HTTPError as exc:  # pragma: no cover - network failure path
            raise OllamaProviderError(
                f"Failed to reach Ollama at {self.base_url}: {exc}"
            ) from exc

        if response.status_code != 200:
            raise OllamaProviderError(
                f"Ollama returned status {response.status_code}: {response.text}"
            )

        data = response.json()
        output = data.get("response", "")
        metadata = {
            "model": data.get("model", model),
            "created_at": data.get("created_at"),
        }
        return CompletionResponse(output=output, metadata=metadata)


registry.register(OllamaProvider)
