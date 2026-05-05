from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Scope:
    """Represents a collection of NodeChunks in a specific scope (Module or Class)."""

    name: str
    chunks: list[NodeChunk]


@dataclass
class NodeChunk:
    """Represents a chunk of code (e.g., a function definition) with its original source lines."""

    name: str
    is_init: bool
    lines: list[str]
    calls: set[str]  # names of local functions/methods called by this chunk
