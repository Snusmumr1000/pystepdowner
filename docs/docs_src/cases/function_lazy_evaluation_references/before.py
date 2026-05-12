def c() -> str:
    return "c"


def b() -> str:
    return "b"


def a(key: str):
    # Lazy evaluation
    d = {"b": b, "c": c}
    # Lazy evaluation
    l = [b, c]
    return d[key](), l
