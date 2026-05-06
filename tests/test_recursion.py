from tests.common import format_code


def test_given_self_recursive_function_when_reformatting_then_it_is_ordered_as_if_non_recursive() -> None:
    # recursive calls helper (and itself), helper calls leaf.
    # correct stepdown order: recursive -> helper -> leaf
    source = """
def leaf():
    pass


def helper():
    leaf()


def recursive(items):
    if items:
        recursive(items[1:])
    helper()
"""
    expected = """
def recursive(items):
    if items:
        recursive(items[1:])
    helper()


def helper():
    leaf()


def leaf():
    pass
"""
    assert format_code(source) == expected.strip("\n")


def test_given_mutually_recursive_functions_when_reformatting_then_they_maintain_caller_first_order_without_deferral() -> None:
    # When two functions are mutually recursive (A calls B, B calls A),
    # the cycle should not cause them to be deferred after leaf helpers.
    source = """
def top():
    heavy()
    light()


def light():
    pass


def heavy():
    helper()


def helper():
    heavy()
"""
    # heavy calls helper (and helper calls heavy back — mutual recursion).
    # Stepdown: top → heavy → helper → light
    expected = """
def top():
    heavy()
    light()


def heavy():
    helper()


def helper():
    heavy()


def light():
    pass
"""
    assert format_code(source) == expected.strip("\n")


def test_given_mutually_recursive_cycle_and_larger_sibling_when_reformatting_then_cycle_is_not_pushed_to_bottom() -> None:
    # When an orchestrator calls a mutually-recursive helper AND a larger
    # helper, the recursive one should still appear in the stepdown order
    # near its caller.
    source = """
def orchestrator():
    recursive_helper()
    big_helper()


def big_helper():
    sub_a()
    sub_b()


def sub_a():
    pass


def sub_b():
    pass


def recursive_helper():
    partner()


def partner():
    recursive_helper()
"""
    expected = """
def orchestrator():
    recursive_helper()
    big_helper()


def recursive_helper():
    partner()


def partner():
    recursive_helper()


def big_helper():
    sub_a()
    sub_b()


def sub_a():
    pass


def sub_b():
    pass
"""
    assert format_code(source) == expected.strip("\n")
