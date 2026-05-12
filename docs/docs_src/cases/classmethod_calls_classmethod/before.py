class Greeting:
    @classmethod
    def format_name(cls) -> str:
        return "Ada"

    @classmethod
    def greet(cls) -> str:
        return f"Hello, {cls.format_name()}!"
