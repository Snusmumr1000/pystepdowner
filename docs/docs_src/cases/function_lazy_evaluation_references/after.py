def a(key: str):
    # Lazy evaluation
    d = {"b": b, "c": c}
    # Lazy evaluation
    l = [b, c]
    return d[key](), l


def b() -> str:
    return "b"


def c() -> str:
    return "c"
