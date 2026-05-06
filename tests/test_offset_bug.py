from pystepdowner.analyzer import reformat_content


def test_offset_bug_nested_shrinking() -> None:
    content = """class MyClass:
    def method_a(self):
        pass



    def method_b(self):
        self.method_a()

def outer_func():
    MyClass()
"""
    expected = """def outer_func():
    MyClass()


class MyClass:
    def method_b(self):
        self.method_a()

    def method_a(self):
        pass

"""
    formatted = reformat_content(content)
    assert formatted == expected
