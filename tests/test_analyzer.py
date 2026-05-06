from pystepdowner.analyzer import reformat_content


def test_valid_order() -> None:
    source = """
def a():
    b()


def b():
    pass
"""
    assert format_code(source) == source.strip("\n")


def test_invalid_order_is_corrected() -> None:
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


def test_invalid_order_is_corrected_for_double_or_more_uses() -> None:
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


def test_invalid_order_is_corrected_for_nested_functions() -> None:
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


def test_init_always_first() -> None:
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


def test_function_assignments_static() -> None:
    source = """
def meh() -> None:
    pass


class A:
    heh = meh


A.heh()
"""
    expected = source
    assert format_code(source) == expected.strip("\n")


def test_function_assignments_dynamic() -> None:
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


def test_multiple_roots_sorted_by_out_degree() -> None:
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


def test_retains_comments_and_decorators() -> None:
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


def test_cls_calls() -> None:
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


def test_mixed_approach_method_calls_module_function() -> None:
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


def test_class_type_dependencies() -> None:
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


def test_real_world_cli_script() -> None:
    source = """
from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str


class UserService:
    def fetch_user(self, uid: int) -> User:
        return User(id=uid, name="Alice")


def main():
    service = UserService()
    user = service.fetch_user(1)
    print(user)


if __name__ == "__main__":
    main()
"""
    expected = """
from __future__ import annotations


from dataclasses import dataclass


def main():
    service = UserService()
    user = service.fetch_user(1)
    print(user)


class UserService:
    def fetch_user(self, uid: int) -> User:
        return User(id=uid, name="Alice")


@dataclass
class User:
    id: int
    name: str


if __name__ == "__main__":
    main()
"""
    assert format_code(source) == expected.strip("\n")


def test_real_world_api_router() -> None:
    source = """
class ItemRequest:
    name: str


def _validate_name(name: str) -> bool:
    return len(name) > 0


class ItemController:
    def handle(self, req: ItemRequest):
        if not _validate_name(req.name):
            raise ValueError()


def post_item():
    ctrl = ItemController()
    ctrl.handle(ItemRequest(name="test"))
"""
    expected = """
from __future__ import annotations


def post_item():
    ctrl = ItemController()
    ctrl.handle(ItemRequest(name="test"))


class ItemController:
    def handle(self, req: ItemRequest):
        if not _validate_name(req.name):
            raise ValueError()


class ItemRequest:
    name: str


def _validate_name(name: str) -> bool:
    return len(name) > 0
"""
    assert format_code(source) == expected.strip("\n")


def test_real_world_repository_pattern() -> None:
    source = """
@dataclass
class Config:
    db_url: str


class Database:
    def __init__(self, cfg: Config):
        self.url = cfg.db_url


class UserRepository:
    def __init__(self, db: Database):
        self.db = db
    
    def get(self) -> User:
        return User()


class User:
    pass


class Application:
    def __init__(self):
        self.cfg = Config("sqlite://")
        self.db = Database(self.cfg)
        self.repo = UserRepository(self.db)
        
    def run(self):
        self.repo.get()
"""
    # Kahn's algorithm resolves:
    # App -> Config, Database, UserRepository
    # Database -> Config
    # UserRepository -> Database, User
    # Valid output ensures A comes before B if A -> B
    expected = """
from __future__ import annotations


class Application:
    def __init__(self):
        self.cfg = Config("sqlite://")
        self.db = Database(self.cfg)
        self.repo = UserRepository(self.db)
        
    def run(self):
        self.repo.get()


class UserRepository:
    def __init__(self, db: Database):
        self.db = db
    
    def get(self) -> User:
        return User()


class Database:
    def __init__(self, cfg: Config):
        self.url = cfg.db_url


@dataclass
class Config:
    db_url: str


class User:
    pass
"""
    assert format_code(source) == expected.strip("\n")


def test_future_annotations_inserted() -> None:
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


def test_recursive_function_does_not_block_ordering() -> None:
    # process_body calls itself recursively. The self-call must not inflate
    # in_degree, otherwise process_body would never become a root and the
    # entire subgraph (extract_chunks, get_calls, ...) would fall into the
    # cycle-fallback path — producing wrong output order.
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
    # recursive calls helper (and itself), helper calls leaf.
    # correct stepdown order: recursive -> helper -> leaf
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


def test_future_annotations_idempotent() -> None:
    source = """
from __future__ import annotations


def process(a: MyClass):
    pass


class MyClass:
    pass
"""
    # Should not duplicate the import
    expected = """
from __future__ import annotations


def process(a: MyClass):
    pass


class MyClass:
    pass
"""
    assert format_code(source) == expected.strip("\n")


def test_mutual_recursion_does_not_defer_ordering() -> None:
    # When two functions are mutually recursive (A calls B, B calls A),
    # the cycle should not cause them to be deferred after leaf helpers.
    # This reproduces a real bug where process_body ↔ _recurse_class_bodies
    # formed a cycle and got pushed after _has_future_annotations.
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


def test_mutually_recursive_callee_not_deferred_by_big_sibling() -> None:
    # When an orchestrator calls a mutually-recursive helper AND a larger
    # helper, the recursive one should still appear in the stepdown order
    # near its caller — not be deferred to the bottom because its cycle
    # partner keeps its in-degree elevated.
    # This reproduces the bug where process_body's call to _recurse_class_bodies
    # (which calls process_body back) was placed at the bottom of analyzer.py.
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
    # DFS from orchestrator:
    #   big_helper (broader subtree) → sub_a → sub_b
    #   recursive_helper → partner (cycle back to recursive_helper, skip)
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


def test_inheritance_is_not_a_call_dependency() -> None:
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


def format_code(source: str) -> str:
    return reformat_content(source.strip("\n")).strip("\n")
