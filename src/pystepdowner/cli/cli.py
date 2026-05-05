from pathlib import Path
from typing import Annotated

import typer

from pystepdowner.analyzer import reformat_content
from pystepdowner.cli.common import _error_handler

app = typer.Typer(help="Enforce stepdown rule in Python files")


@app.command()
@_error_handler
def fmt(
    in_file: Annotated[Path, typer.Option("-i", "--in-file", help="Input file to format", exists=True, dir_okay=False)],
) -> None:
    """
    Format a Python file according to the Stepdown rule.
    """
    reformatted_content = _format(in_file)
    typer.echo(reformatted_content)


@app.command()
@_error_handler
def rw(
    in_path: Annotated[Path, typer.Option("-i", "--in-path", help="Input file or directory to format", exists=True, dir_okay=True)],
    out_path: Annotated[Path | None, typer.Option("-o", "--out-path", help="Output file or directory to write to", dir_okay=True)] = None,
) -> None:
    """
    Rewrite a Python file according to the Stepdown rule and write the result to an output file.
    """
    match in_path:
        case Path() if in_path.is_dir():
            # recursively process all Python files in the directory
            for file_path in in_path.rglob("*.py"):
                reformatted_content = _format(file_path)
                file_path.write_text(reformatted_content, encoding="utf-8")
            return
        case Path() if in_path.is_file():
            reformatted_content = _format(in_path)
            target_out_file = out_path or in_path
            target_out_file.write_text(reformatted_content, encoding="utf-8")
            return
        case _:
            typer.echo("Invalid path", err=True)
            raise typer.Exit(code=1)


def _format(in_file: Path) -> str:
    in_file_content = in_file.read_text(encoding="utf-8")
    return reformat_content(in_file_content)


if __name__ == "__main__":
    app()
