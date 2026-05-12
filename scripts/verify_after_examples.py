from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from sys import stdout
from typing import Annotated

import typer

from pystepdowner.analyzer import reformat_content


def main(
    root: Annotated[Path, typer.Argument(help="Root directory to scan.")] = Path("docs_src"),
) -> None:
    """Verify sibling before.py and after.py example pairs."""
    result = verify_after_examples(root)
    if result.failures:
        stdout.write("\n".join(result.failures) + "\n")
        raise typer.Exit(code=1)

    stdout.write(f"verified {result.count} before.py/after.py pair(s)\n")


def verify_after_examples(root: Path) -> VerificationResult:
    failures = []
    count = 0
    for before_file in sorted(root.rglob("before.py")):
        failures.extend(verify_after_example(before_file))
        count += 1
    return VerificationResult(count=count, failures=failures)


def verify_after_example(before_file: Path) -> list[str]:
    after_file = before_file.with_name("after.py")
    failures = verify_python_syntax(before_file)
    before_content = before_file.read_text(encoding="utf-8")
    expected = reformat_content(before_content)
    if not after_file.exists():
        return [*failures, f"{after_file}: missing"]
    after_content = after_file.read_text(encoding="utf-8")
    failures.extend(verify_python_syntax(after_file))
    if after_content != expected:
        failures.append(f"{after_file}: does not match formatted {before_file}")
    return failures


def verify_python_syntax(file_path: Path) -> list[str]:
    try:
        ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
    except SyntaxError as exc:
        return [f"{file_path}: invalid Python syntax: {exc.msg} at line {exc.lineno}"]
    return []


@dataclass(frozen=True)
class VerificationResult:
    count: int
    failures: list[str]


if __name__ == "__main__":
    typer.run(main)
