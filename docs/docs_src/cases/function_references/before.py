def d() -> str:
    return "d"


def c() -> str:
    return "c"


def b() -> str:
    return "b"


def a(key: str):
    res = b()
    mapping = {"c": c}
    sequence = [d]
    return res, mapping[key](), sequence
