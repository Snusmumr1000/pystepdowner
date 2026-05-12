def load_user(user_id: int) -> dict:
    return {"id": user_id, "name": "Alice"}


def format_user(user: dict) -> str:
    return f"{user['id']}: {user['name']}"


def user_controller(user_id: int) -> dict:
    user = load_user(user_id)
    return {"body": format_user(user)}
