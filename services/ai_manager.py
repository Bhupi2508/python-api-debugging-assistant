"""AI manager.

Single entry point for the rest of the application to call an AI provider.

Business logic must never import a specific provider (OpenAI/Gemini/Ollama).
"""

from __future__ import annotations

from services.providers.base_provider import AIProvider
from services.providers.ollama_provider import OllamaProvider
from services.providers.openai_provider import OpenAIProvider
from services.providers.gemini_provider import GeminiProvider
from services.providers.claude_provider import ClaudeProvider

from config import load_ai_config


def get_ai_provider() -> AIProvider:
    """Instantiate the configured AI provider."""

    config = load_ai_config()

    if config.provider == "ollama":
        return OllamaProvider(
            base_url=config.ollama_base_url,
            model=config.model,
            timeout_seconds=config.request_timeout_seconds,
        )

    if config.provider == "openai":
        # Read keys from .env via process environment.
        import os

        return OpenAIProvider(
            api_key=(os.getenv("OPENAI_API_KEY") or "").strip() or None,
            model=config.model,
            base_url=(os.getenv("OPENAI_BASE_URL") or "").strip() or None,
            timeout_seconds=config.request_timeout_seconds,
        )

    if config.provider == "gemini":
        import os

        return GeminiProvider(
            api_key=(os.getenv("GEMINI_API_KEY") or "").strip() or None,
            model=config.model,
            timeout_seconds=config.request_timeout_seconds,
        )

    if config.provider == "claude":
        import os

        return ClaudeProvider(
            api_key=(os.getenv("CLAUDE_API_KEY") or "").strip() or None,
            model=config.model,
            timeout_seconds=config.request_timeout_seconds,
        )

    # load_ai_config already validates supported providers, but keep safe.
    raise ValueError(f"Unsupported provider in runtime: {config.provider}")


def complete(prompt: str) -> str:
    """Complete a single prompt and return the provider's response text."""

    provider = get_ai_provider()
    return provider.complete(prompt)
