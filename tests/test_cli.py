from dataclasses import dataclass
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


SOURCE_CODE_1 = """
def b():
    pass


def a():
    b()
"""

EXPECTED_CODE_1 = """
def a():
    b()


def b():
    pass
"""

SOURCE_CODE_2 = """
class A:
    def b(self):
        pass

    def __init__(self):
        self.b()
"""

EXPECTED_CODE_2 = """
class A:
    def __init__(self):
        self.b()

    def b(self):
        pass
"""


@dataclass
class FileFixture:
    file_path: str
    content: str
    expected_content: str

    def setup(self, base_dir: Path) -> Path:
        full_path = base_dir / self.file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(self.content.strip("\n"), encoding="utf-8")
        return full_path

    def verify(self, base_dir: Path) -> None:
        full_path = base_dir / self.file_path
        actual = full_path.read_text(encoding="utf-8").strip("\n")
        assert actual == self.expected_content.strip("\n")


def test_rw_single_file_in_place(tmp_path: Path) -> None:
    fixture = FileFixture("test_1.py", SOURCE_CODE_1, EXPECTED_CODE_1)
    in_file = fixture.setup(tmp_path)

    result = runner.invoke(app, ["rw", "-i", str(in_file)])

    assert result.exit_code == 0
    fixture.verify(tmp_path)


def test_rw_single_file_with_output(tmp_path: Path) -> None:
    in_fixture = FileFixture("test_2.py", SOURCE_CODE_1, SOURCE_CODE_1)
    out_fixture = FileFixture("out_2.py", "", EXPECTED_CODE_1)

    in_file = in_fixture.setup(tmp_path)
    out_file = tmp_path / out_fixture.file_path

    result = runner.invoke(app, ["rw", "-i", str(in_file), "-o", str(out_file)])

    assert result.exit_code == 0
    in_fixture.verify(tmp_path)
    out_fixture.verify(tmp_path)


def test_rw_directory_recursive(tmp_path: Path) -> None:
    fixtures = [
        FileFixture("dir1/file1.py", SOURCE_CODE_1, EXPECTED_CODE_1),
        FileFixture("dir2/file2.py", SOURCE_CODE_2, EXPECTED_CODE_2),
        FileFixture("dir2/file3.txt", SOURCE_CODE_1, SOURCE_CODE_1),
    ]

    for fixture in fixtures:
        fixture.setup(tmp_path)

    result = runner.invoke(app, ["rw", "-i", str(tmp_path)])

    assert result.exit_code == 0
    for fixture in fixtures:
        fixture.verify(tmp_path)
