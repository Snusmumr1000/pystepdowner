def a(key: str):
    res = b()
    mapping = {"c": c}
    sequence = [d]
    return res, mapping[key](), sequence


def b() -> str:
    return "b"


def c() -> str:
    return "c"


def d() -> str:
    return "d"
