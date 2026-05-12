def c() -> str:
    return "c"


def b() -> str:
    return "b"


def a(key: str) -> str:
    handlers = {"b": b, "c": c}
    handler = handlers[key]
    return handler()
