from __future__ import annotations

from typing import Dict, Optional, Type

from .types import LLMProvider


class ProviderRegistry:
    """Runtime registry for provider adapters."""

    def __init__(self) -> None:
        self._providers: Dict[str, Type[LLMProvider]] = {}

    def register(self, provider_cls: Type[LLMProvider]) -> None:
        key = provider_cls.name.lower()
        if key in self._providers:
            raise ValueError(f"Provider '{provider_cls.name}' already registered")
        self._providers[key] = provider_cls

    def create(self, name: str, **kwargs) -> LLMProvider:
        provider = self._providers.get(name.lower())
        if provider is None:
            raise KeyError(f"No LLM provider registered under name '{name}'")
        return provider(**kwargs)

    def get(self, name: str) -> Optional[Type[LLMProvider]]:
        return self._providers.get(name.lower())

    def available(self) -> list[str]:
        return sorted(self._providers.keys())


registry = ProviderRegistry()
