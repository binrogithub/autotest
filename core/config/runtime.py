"""Runtime configuration for tool execution.

This module avoids optional dependencies and keeps behavior deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import count
from typing import Callable

_run_counter = count(1)


def next_run_id() -> str:
    """Return a deterministic, incrementing run id."""
    return f"run-{next(_run_counter)}"


@dataclass(frozen=True)
class RuntimeConfig:
    """Configuration for tool registry and runner behavior."""

    allow_tool_overwrite: bool = False
    default_stage: str = "run"
    run_id_factory: Callable[[], str] = next_run_id


_runtime_config = RuntimeConfig()


def get_runtime_config() -> RuntimeConfig:
    """Return the current runtime configuration."""
    return _runtime_config


def configure_runtime(**overrides: object) -> RuntimeConfig:
    """Update runtime configuration deterministically.

    Returns the updated config so callers can chain or store it.
    """
    global _runtime_config
    _runtime_config = replace(_runtime_config, **overrides)
    return _runtime_config
