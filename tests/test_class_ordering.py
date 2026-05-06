from tests.common import format_code


def test_given_class_with_out_of_order_methods_when_reformatting_then_init_remains_the_first_method() -> None:
    source = """
class A:
    def b(self):
        pass

    def __init__(self):
        self.b()
"""
    expected = """
class A:
    def __init__(self):
        self.b()

    def b(self):
        pass
"""
    assert format_code(source) == expected.strip("\n")


def test_given_class_with_classmethod_calls_via_cls_when_reformatting_then_dependency_is_correctly_ordered() -> None:
    source = """
class A:
    @classmethod
    def b(cls):
        pass

    @classmethod
    def a(cls):
        cls.b()
"""
    expected = """
class A:
    @classmethod
    def a(cls):
        cls.b()

    @classmethod
    def b(cls):
        pass
"""
    assert format_code(source) == expected.strip("\n")


def test_given_class_method_calling_module_function_when_reformatting_then_class_precedes_module_function() -> None:
    # A class method calls a module-level function.
    # The stepdown analyzer recursively evaluates the class body and
    # adds module_func to the calls for class A, effectively ranking A above it.
    source = """
def module_func():
    pass


class A:
    def method(self):
        module_func()
"""
    expected = """
class A:
    def method(self):
        module_func()


def module_func():
    pass
"""
    assert format_code(source) == expected.strip("\n")


def test_given_inheritance_relationship_when_reformatting_then_base_class_precedes_child_class() -> None:
    source = """
class Base:
    pass


class Child(Base):
    pass
"""
    expected = """
class Base:
    pass


class Child(Base):
    pass
"""
    assert format_code(source) == expected.strip("\n")
