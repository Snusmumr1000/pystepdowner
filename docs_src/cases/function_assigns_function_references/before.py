def b() -> str:
    return "b"


def c() -> str:
    return "c"


def a() -> list[object]:
    handlers = [b, c]
    return handlers
