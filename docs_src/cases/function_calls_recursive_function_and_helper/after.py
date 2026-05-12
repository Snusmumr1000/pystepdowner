def recursive(items: list[str]) -> str:
    if items:
        return recursive(items[1:])
    return helper()


def helper() -> str:
    return leaf()


def leaf() -> str:
    return "leaf"
