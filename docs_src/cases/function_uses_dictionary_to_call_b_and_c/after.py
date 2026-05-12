def a(key: str) -> str:
    handlers = {"b": b, "c": c}
    handler = handlers[key]
    return handler()


def b() -> str:
    return "b"


def c() -> str:
    return "c"
