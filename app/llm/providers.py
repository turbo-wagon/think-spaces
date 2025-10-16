from __future__ import annotations

from dataclasses import dataclass

from .registry import registry
from .types import CompletionRequest, CompletionResponse, LLMProvider


@dataclass
class EchoProvider(LLMProvider):
    """Fallback provider that simply echoes prompts. Useful for tests."""

    name: str = "echo"

    async def generate(self, request: CompletionRequest) -> CompletionResponse:
        combined_context = "\n".join(request.context)
        output = "\n".join(
            part
            for part in (
                f"[system]\n{request.system}" if request.system else None,
                combined_context if combined_context else None,
                request.prompt,
            )
            if part
        )
        return CompletionResponse(output=output or "")


# Register default provider
registry.register(EchoProvider)
