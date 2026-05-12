class Greeting:
    @staticmethod
    def format_name() -> str:
        return "Ada"

    def greet(self) -> str:
        return f"Hello, {self.format_name()}!"
