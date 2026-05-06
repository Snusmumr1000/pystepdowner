from tests.common import format_code


def test_given_correctly_ordered_functions_when_reformatting_then_content_remains_unchanged() -> None:
    source = """
def a():
    b()


def b():
    pass
"""
    assert format_code(source) == source.strip("\n")


def test_given_callee_before_caller_when_reformatting_then_callee_is_moved_after_caller() -> None:
    source = """
def b():
    pass


def a():
    b()
"""
    expected = """
def a():
    b()


def b():
    pass
"""
    assert format_code(source) == expected.strip("\n")


def test_given_multiple_callers_for_same_callee_when_reformatting_then_callee_is_moved_after_all_callers() -> None:
    source = """
def b():
    pass


def c():
    b()


def a():
    b()
"""
    expected = """
def c():
    b()


def a():
    b()


def b():
    pass
"""
    assert format_code(source) == expected.strip("\n")


def test_given_multiple_independent_roots_when_reformatting_then_they_are_ordered_by_out_degree_descending() -> None:
    source = """
def root2():
    pass


def root1():
    child1()
    child2()


def child1():
    pass


def child2():
    pass
"""
    # root1 calls 2 things, root2 calls 0 things.
    # root1 should precede root2.
    expected = """
def root1():
    child1()
    child2()


def child1():
    pass


def child2():
    pass


def root2():
    pass
"""
    assert format_code(source) == expected.strip("\n")
