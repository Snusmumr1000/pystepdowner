def a(key: str):
    # Direct call
    res = b()
    # Lazy evaluation
    mapping = {"c": c}
    # Lazy evaluation
    sequence = [d]
    return res, mapping[key](), sequence


def b() -> str:
    return "b"


def c() -> str:
    return "c"


def d() -> str:
    return "d"
