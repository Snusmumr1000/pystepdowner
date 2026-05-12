from __future__ import annotations

from pathlib import Path
from sys import stdout
from typing import Annotated

import typer

from pystepdowner.analyzer import reformat_content


def main(
    root: Annotated[Path, typer.Argument(help="Root directory to scan.")] = Path("docs_src"),
) -> None:
    """Regenerate sibling after.py examples from before.py files."""
    count = update_after_examples(root)
    stdout.write(f"updated {count} after.py file(s)\n")


def update_after_examples(root: Path) -> int:
    count = 0
    for before_file in sorted(root.rglob("before.py")):
        update_after_example(before_file)
        count += 1
    return count


def update_after_example(before_file: Path) -> None:
    after_file = before_file.with_name("after.py")
    after_file.write_text(reformat_content(before_file.read_text(encoding="utf-8")), encoding="utf-8")
    stdout.write(f"{after_file}\n")


if __name__ == "__main__":
    typer.run(main)
