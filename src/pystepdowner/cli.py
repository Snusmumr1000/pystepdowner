from pathlib import Path
from typing import Annotated

import typer

from pystepdowner.analyzer import reformat_file

app = typer.Typer(help="Enforce stepdown rule in Python files")


@app.command(name="format")
def format_files(
    path: Annotated[Path, typer.Argument(exists=True, help="File or directory to format")],
) -> None:
    """
    Format Python files according to the Stepdown rule.
    """
    files = []
    if path.is_file():
        if path.suffix == ".py":
            files.append(path)
    elif path.is_dir():
        files.extend(path.rglob("*.py"))

    changed_count = 0
    for file in files:
        try:
            modified = reformat_file(str(file))
            if modified:
                typer.echo(f"Reformatted {file}")
                changed_count += 1
        except Exception as e:
            typer.echo(f"Error processing {file}: {e}", err=True)

    typer.echo(f"Done. {changed_count} files modified.")


if __name__ == "__main__":
    app()
