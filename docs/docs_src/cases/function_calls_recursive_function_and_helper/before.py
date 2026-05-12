def leaf() -> str:
    return "leaf"


def helper() -> str:
    return leaf()


def recursive(items: list[str]) -> str:
    if items:
        return recursive(items[1:])
    return helper()
