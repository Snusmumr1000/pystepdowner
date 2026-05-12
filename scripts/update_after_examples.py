from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from sys import stdout
from typing import Annotated

import typer

from pystepdowner.analyzer import reformat_content


def main(
    root: Annotated[Path, typer.Argument(help="Root directory to scan.")] = Path("docs_src"),
) -> None:
    """Regenerate sibling after.py examples from before.py files."""
    result = update_after_examples(root)
    stdout.write(f"scanned {result.scanned} before.py file(s), updated {result.updated} after.py file(s)\n")


def update_after_examples(root: Path) -> UpdateResult:
    scanned = 0
    updated = 0
    for before_file in sorted(root.rglob("before.py")):
        if update_after_example(before_file):
            updated += 1
        scanned += 1
    return UpdateResult(scanned=scanned, updated=updated)


def update_after_example(before_file: Path) -> bool:
    after_file = before_file.with_name("after.py")
    content = reformat_content(before_file.read_text(encoding="utf-8"))
    if after_file.exists() and after_file.read_text(encoding="utf-8") == content:
        return False
    after_file.write_text(content, encoding="utf-8")
    stdout.write(f"{after_file}\n")
    return True


@dataclass(frozen=True)
class UpdateResult:
    scanned: int
    updated: int


if __name__ == "__main__":
    typer.run(main)
