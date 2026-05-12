def b() -> str:
    return "b"


def a(key: str) -> str:
    handlers = {"b": b}
    handler = handlers[key]
    return handler()
