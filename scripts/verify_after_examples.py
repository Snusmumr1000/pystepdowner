from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from sys import stdout

from pystepdowner.analyzer import reformat_content


def main() -> int:
    parser = ArgumentParser(description="Verify sibling before.py and after.py example pairs.")
    parser.add_argument("root", nargs="?", default="docs_src", type=Path, help="Root directory to scan.")
    args = parser.parse_args()

    failures = []
    count = 0
    for before_file in sorted(args.root.rglob("before.py")):
        after_file = before_file.with_name("after.py")
        expected = reformat_content(before_file.read_text(encoding="utf-8"))
        if not after_file.exists():
            failures.append(f"{after_file}: missing")
        elif after_file.read_text(encoding="utf-8") != expected:
            failures.append(f"{after_file}: does not match formatted {before_file}")
        count += 1

    if failures:
        stdout.write("\n".join(failures) + "\n")
        return 1

    stdout.write(f"verified {count} before.py/after.py pair(s)\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
