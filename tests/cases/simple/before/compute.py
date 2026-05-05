def add(a: float, b: float) -> float:
    return a + b


def mul(a: float, b: float) -> float:
    res = 0
    for _ in range(b):
        res = add(res, a)
    return res


def sub(a: float, b: float) -> float:
    return a - b


def pow(a: float, b: int) -> float:
    res = 1
    for _ in range(b):
        res = mul(res, a)
    return res
