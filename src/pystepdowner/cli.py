from pathlib import Path
from typing import Annotated

import typer

from pystepdowner.analyzer import reformat_content

app = typer.Typer(help="Enforce stepdown rule in Python files")


@app.command(name="format")
def format_files(
    in_file: Annotated[Path, typer.Option("-i", "--in-file", help="Input file to format", exists=True, dir_okay=False)],
) -> None:
    """
    Format a Python file according to the Stepdown rule.
    """
    try:
        in_file_content = in_file.read_text(encoding="utf-8")
        reformatted_content = reformat_content(in_file_content)
        typer.echo(reformatted_content)
    except Exception as e:
        typer.echo(f"Error processing {in_file}: {e}", err=True)


if __name__ == "__main__":
    app()
