def c() -> str:
    return "c"


def b() -> str:
    return "b"


def a() -> str:
    return b() + c()
