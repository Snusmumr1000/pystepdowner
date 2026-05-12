class Greeting:
    @classmethod
    def greet(cls) -> str:
        return f"Hello, {cls.format_name()}!"

    @classmethod
    def format_name(cls) -> str:
        return "Ada"
