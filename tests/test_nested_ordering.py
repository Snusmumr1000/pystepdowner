from tests.common import format_code


def test_given_nested_functions_with_incorrect_order_when_reformatting_then_internal_stepdown_rule_is_applied() -> None:
    source = """
def a():
    def b():
        def d():
            pass

        def e():
            d()

        e()

    def c():
        b()
    
    c()
"""
    expected = """
def a():
    def c():
        b()

    def b():
        def e():
            d()

        def d():
            pass

        e()
    
    c()
"""
    assert format_code(source) == expected.strip("\n")
