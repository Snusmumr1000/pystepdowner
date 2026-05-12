class User:
    pass


def process(user: User) -> str:
    return user.__class__.__name__
