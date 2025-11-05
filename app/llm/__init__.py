"""LLM provider registry and utilities."""

from .registry import ProviderRegistry, registry
from .types import CompletionRequest, CompletionResponse, LLMProvider
# Ensure default providers register on import
from . import providers  # noqa: F401

try:  # noqa: SIM105
    from . import openai_provider  # noqa: F401
except Exception:  # pragma: no cover - optional dependency guard
    pass

try:  # noqa: SIM105
    from . import ollama_provider  # noqa: F401
except Exception:  # pragma: no cover - optional dependency guard
    pass

try:  # noqa: SIM105
    from . import groq_provider  # noqa: F401
except Exception:  # pragma: no cover - optional dependency guard
    pass

__all__ = [
    "ProviderRegistry",
    "registry",
    "CompletionRequest",
    "CompletionResponse",
    "LLMProvider",
]
