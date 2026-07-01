"""Lightweight logging for Phase 2.

Avoids external dependencies and does not log sensitive data such as
API keys or full request bodies.
"""

from __future__ import annotations

from datetime import datetime


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def info(message: str) -> None:
    print(f"[INFO] {_timestamp()} {message}")


def warning(message: str) -> None:
    print(f"[WARN] {_timestamp()} {message}")


def error(message: str) -> None:
    print(f"[ERROR] {_timestamp()} {message}")
