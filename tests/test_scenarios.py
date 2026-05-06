from tests.common import format_code


def test_scenario_given_cli_script_when_reformatting_then_it_follows_stepdown_rule() -> None:
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


def test_scenario_given_api_router_when_reformatting_then_it_follows_stepdown_rule() -> None:
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


def test_scenario_given_repository_pattern_when_reformatting_then_it_follows_stepdown_rule() -> None:
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


def test_regression_given_nested_class_with_extra_newlines_when_reformatting_then_offsets_remain_correct() -> None:
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
    assert format_code(content) == expected.strip("\n")
