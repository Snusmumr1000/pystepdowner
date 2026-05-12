def a(key: str):
    # Dictionary lazy evaluation
    d = {"b": b, "c": c}
    # List lazy evaluation
    l = [b, c]
    return d[key](), l


def b() -> str:
    return "b"


def c() -> str:
    return "c"
