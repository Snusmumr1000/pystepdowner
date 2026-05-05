from pathlib import Path

import pytest
from typer.testing import CliRunner

from pystepdowner.cli.cli import app

runner = CliRunner()


@pytest.mark.parametrize("filename", ["main.py", "compute.py", "models.py"])
def test_format_file_with_output(filename: str) -> None:
    cases_dir = Path(__file__).parent / "cases" / "simple"
    before_file = cases_dir / "before" / filename
    after_file = cases_dir / "after" / filename

    result = runner.invoke(app, ["fmt", "-i", str(before_file)])

    assert result.exit_code == 0
    assert result.output.strip() == after_file.read_text().strip()
