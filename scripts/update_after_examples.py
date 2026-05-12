from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from sys import stdout

from pystepdowner.analyzer import reformat_content


def main() -> int:
    parser = ArgumentParser(description="Regenerate sibling after.py examples from before.py files.")
    parser.add_argument("root", nargs="?", default="docs_src", type=Path, help="Root directory to scan.")
    args = parser.parse_args()

    count = 0
    for before_file in sorted(args.root.rglob("before.py")):
        after_file = before_file.with_name("after.py")
        after_file.write_text(reformat_content(before_file.read_text(encoding="utf-8")), encoding="utf-8")
        stdout.write(f"{after_file}\n")
        count += 1

    stdout.write(f"updated {count} after.py file(s)\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
