from __future__ import annotations


def process(user: User) -> str:
    return user.__class__.__name__


class User:
    pass
