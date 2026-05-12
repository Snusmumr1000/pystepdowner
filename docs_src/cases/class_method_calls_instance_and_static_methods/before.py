class Greeting:
    @staticmethod
    def format_punctuation() -> str:
        return "!"

    def format_name(self) -> str:
        return "Ada"

    def greet(self) -> str:
        return f"Hello, {self.format_name()}{self.format_punctuation()}"
