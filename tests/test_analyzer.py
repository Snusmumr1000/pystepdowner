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


def format_code(source: str) -> str:
    return reformat_content(source.strip("\n")).strip("\n")


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
