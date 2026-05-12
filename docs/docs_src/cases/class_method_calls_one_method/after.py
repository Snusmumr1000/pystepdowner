class Greeting:
    def greet(self) -> str:
        return f"Hello, {self.format_name()}!"

    def format_name(self) -> str:
        return "Ada"
