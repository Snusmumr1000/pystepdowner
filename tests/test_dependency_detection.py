from tests.common import format_code


def test_given_class_level_function_assignment_when_reformatting_then_it_is_treated_as_dependency() -> None:
    source = """
def meh() -> None:
    pass


class A:
    heh = meh


A.heh()
"""
    expected = source
    assert format_code(source) == expected.strip("\n")


def test_given_local_function_assignment_when_reformatting_then_assigned_function_is_treated_as_dependency() -> None:
    source = """
def cmd1() -> None:
    pass


def cmd2() -> None:
    pass


def main() -> None:
    command1 = cmd1
    command2 = cmd2
    cmds = [command1, command2]
"""
    expected = """
def main() -> None:
    command1 = cmd1
    command2 = cmd2
    cmds = [command1, command2]


def cmd1() -> None:
    pass


def cmd2() -> None:
    pass
"""
    assert format_code(source) == expected.strip("\n")


def test_given_type_annotation_dependency_when_reformatting_then_annotated_class_is_treated_as_dependency() -> None:
    source = """
class B:
     pass


class A:
     b: B
"""
    expected = """
from __future__ import annotations


class A:
     b: B


class B:
     pass
"""
    assert format_code(source) == expected.strip("\n")
