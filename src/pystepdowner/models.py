from dataclasses import dataclass


@dataclass
class NodeChunk:
    """Represents a chunk of code (e.g., a function definition) with its original source lines."""

    name: str
    is_init: bool
    lines: list[str]
    calls: list[str]  # names of local functions/methods called by this chunk
    annotation_calls: list[str]  # names of local functions/methods used in type hints
