"""Configuration loader for Phase 2 AI integration.

Loads settings from a local .env file and exposes a small typed interface
for the rest of the application.

The goal is to keep business logic provider-agnostic.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / ".env"


@dataclass(frozen=True)
class AIConfig:
    """Runtime configuration for AI provider selection and calls."""

    provider: str
    model: str | None
    # Only Ollama needs a base URL for now; cloud providers can use SDK defaults.
    ollama_base_url: str | None
    request_timeout_seconds: int


def load_ai_config() -> AIConfig:
    """Load AI configuration from .env.

    Raises:
        ValueError: if AI_PROVIDER is missing or unsupported.
    """

    # Keep it explicit and beginner-friendly: only load .env if it exists.
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=str(ENV_PATH), override=False)

    provider = (os.getenv("AI_PROVIDER") or "").strip().lower()
    if not provider:
        raise ValueError(
            "AI_PROVIDER is not set. Create a .env file from .env.example."
        )

    request_timeout_seconds = int(os.getenv("REQUEST_TIMEOUT", "60").strip())

    # Provider-specific optional settings.
    # NOTE: We keep this beginner-friendly by resolving a single `model` field
    # from provider-specific env vars.
    model = (
        os.getenv("OLLAMA_MODEL")
        or os.getenv("OPENAI_MODEL")
        or os.getenv("GEMINI_MODEL")
        or os.getenv("CLAUDE_MODEL")
        or ""
    ).strip() or None

    # Provider-specific base URLs (only Ollama needs one for now).
    ollama_base_url = (os.getenv("OLLAMA_BASE_URL") or "").strip() or None

    # Validate provider early.
    supported = {"openai", "gemini", "claude", "ollama"}
    if provider not in supported:
        raise ValueError(
            "Invalid AI_PROVIDER='{}' in .env. Supported provider(s): {}".format(
                provider, ", ".join(sorted(supported))
            )
        )

    return AIConfig(
        provider=provider,
        model=model,
        ollama_base_url=ollama_base_url,
        request_timeout_seconds=request_timeout_seconds,
    )
