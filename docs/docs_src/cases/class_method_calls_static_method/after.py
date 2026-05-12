class Greeting:
    def greet(self) -> str:
        return f"Hello, {self.format_name()}!"

    @staticmethod
    def format_name() -> str:
        return "Ada"
