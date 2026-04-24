import ast
import pytest
from pystepdowner.analyzer import process_body

def format_code(source: str) -> str:
    lines = source.split('\n')
    tree = ast.parse(source)
    new_lines, modified = process_body(tree.body, lines)
    return '\n'.join(new_lines)

def test_valid_order():
    source = (
        "def a():\n"
        "    b()\n"
        "def b():\n"
        "    pass\n"
    )
    assert format_code(source) == source

def test_invalid_order_is_corrected():
    source = (
        "def b():\n"
        "    pass\n"
        "def a():\n"
        "    b()\n"
    )
    expected = (
        "def a():\n"
        "    b()\n"
        "def b():\n"
        "    pass\n"
    )
    assert format_code(source) == expected

def test_init_always_first():
    source = (
        "class A:\n"
        "    def b(self):\n"
        "        pass\n"
        "    def __init__(self):\n"
        "        self.b()\n"
    )
    expected = (
        "class A:\n"
        "    def __init__(self):\n"
        "        self.b()\n"
        "    def b(self):\n"
        "        pass\n"
    )
    assert format_code(source) == expected

def test_multiple_roots_sorted_by_out_degree():
    source = (
        "def root2():\n"
        "    pass\n"
        "def root1():\n"
        "    child1()\n"
        "    child2()\n"
        "def child1():\n"
        "    pass\n"
        "def child2():\n"
        "    pass\n"
    )
    # root1 calls 2 things, root2 calls 0 things.
    # root1 should precede root2.
    expected = (
        "def root1():\n"
        "    child1()\n"
        "    child2()\n"
        "def child1():\n"
        "    pass\n"
        "def child2():\n"
        "    pass\n"
        "def root2():\n"
        "    pass\n"
    )
    assert format_code(source) == expected

def test_retains_comments_and_decorators():
    source = (
        "@deco\n"
        "def b():\n"
        "    pass\n"
        "# Comment for a\n"
        "def a():\n"
        "    b()\n"
    )
    expected = (
        "# Comment for a\n"
        "def a():\n"
        "    b()\n"
        "@deco\n"
        "def b():\n"
        "    pass\n"
    )
    assert format_code(source) == expected

def test_cls_calls():
    source = (
        "class A:\n"
        "    @classmethod\n"
        "    def b(cls):\n"
        "        pass\n"
        "    @classmethod\n"
        "    def a(cls):\n"
        "        cls.b()\n"
    )
    expected = (
        "class A:\n"
        "    @classmethod\n"
        "    def a(cls):\n"
        "        cls.b()\n"
        "    @classmethod\n"
        "    def b(cls):\n"
        "        pass\n"
    )
    assert format_code(source) == expected
