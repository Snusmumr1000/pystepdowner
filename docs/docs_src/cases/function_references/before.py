def d() -> str:
    return "d"


def c() -> str:
    return "c"


def b() -> str:
    return "b"


def a(key: str):
    # Direct call
    res = b()
    # Lazy evaluation
    mapping = {"c": c}
    # Lazy evaluation
    sequence = [d]
    return res, mapping[key](), sequence
