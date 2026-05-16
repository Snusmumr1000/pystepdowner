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


def test_given_class_level_default_references_function_when_reformatting_then_function_stays_before_class() -> None:
    source = """
def my_func() -> None:
    pass


class Foo:
    func = my_func


def main() -> None:
    Foo()
"""
    expected = """
def main() -> None:
    Foo()


def my_func() -> None:
    pass


class Foo:
    func = my_func
"""
    assert format_code(source) == expected.strip("\n")


def test_given_default_argument_references_function_when_reformatting_then_default_stays_defined_first() -> None:
    source = """
def formatter(value: str) -> str:
    return value.upper()


def greet(formatter=formatter) -> str:
    return formatter("hi")


def main() -> None:
    greet()
"""
    expected = """
def main() -> None:
    greet()


def formatter(value: str) -> str:
    return value.upper()


def greet(formatter=formatter) -> str:
    return formatter("hi")
"""
    assert format_code(source) == expected.strip("\n")


def test_given_decorator_references_function_when_reformatting_then_decorator_stays_defined_first() -> None:
    source = """
def my_decorator(func):
    return func


@my_decorator
def task() -> None:
    pass


def main() -> None:
    task()
"""
    expected = """
def main() -> None:
    task()


def my_decorator(func):
    return func


@my_decorator
def task() -> None:
    pass
"""
    assert format_code(source) == expected.strip("\n")


def test_given_init_default_references_method_when_reformatting_then_dependency_stays_before_init() -> None:
    source = """
class A:
    def helper(self):
        pass

    def __init__(self, helper=helper):
        self.helper = helper
"""
    expected = source
    assert format_code(source) == expected.strip("\n")


def test_given_init_decorator_references_method_when_reformatting_then_dependency_stays_before_init() -> None:
    source = """
class A:
    def decorate(func):
        return func

    @decorate
    def __init__(self):
        pass
"""
    expected = source
    assert format_code(source) == expected.strip("\n")


def test_given_eager_default_cycle_when_reformatting_then_it_does_not_recurse_forever() -> None:
    source = """
def a(value=b):
    pass


def b(value=a):
    pass
"""
    expected = """
def b(value=a):
    pass


def a(value=b):
    pass
"""
    assert format_code(source) == expected.strip("\n")


def test_given_class_eager_default_cycle_when_reformatting_then_it_does_not_recurse_forever() -> None:
    source = """
class A:
    def a(self, value=b):
        pass

    def b(self, value=a):
        pass
"""
    expected = """
class A:
    def b(self, value=a):
        pass

    def a(self, value=b):
        pass
"""
    assert format_code(source) == expected.strip("\n")
