"""Base AI provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """A provider is responsible for turning a prompt into a response."""

    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Send a prompt and return the response text."""

        raise NotImplementedError
