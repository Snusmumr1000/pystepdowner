from collections.abc import Callable
from functools import wraps
from typing import Any

import typer


def _error_handler(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        in_file = kwargs.get("in_file")
        try:
            return func(*args, **kwargs)
        except Exception as e:
            typer.echo(f"Error processing {in_file}: {e}", err=True)
            raise typer.Exit(code=1) from e

    return wrapper
