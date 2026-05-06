from tests.common import format_code


def test_given_comments_and_decorators_when_reformatting_then_they_are_preserved_with_their_functions() -> None:
    source = """
@deco
def b():
    pass


# Comment for a
def a():
    b()
"""
    expected = """
# Comment for a
def a():
    b()


@deco
def b():
    pass
"""
    assert format_code(source) == expected.strip("\n")


def test_given_out_of_order_dependencies_requiring_annotations_when_reformatting_then_future_annotations_is_added() -> None:
    source = """
def process(a: MyClass):
    pass


class MyClass:
    pass
"""
    expected = """
from __future__ import annotations


def process(a: MyClass):
    pass


class MyClass:
    pass
"""
    assert format_code(source) == expected.strip("\n")


def test_given_existing_future_annotations_when_reformatting_then_it_is_not_duplicated() -> None:
    source = """
from __future__ import annotations


def process(a: MyClass):
    pass


class MyClass:
    pass
"""
    expected = """
from __future__ import annotations


def process(a: MyClass):
    pass


class MyClass:
    pass
"""
    assert format_code(source) == expected.strip("\n")
