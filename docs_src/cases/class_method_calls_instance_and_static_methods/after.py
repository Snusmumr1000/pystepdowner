class Greeting:
    def greet(self) -> str:
        return f"Hello, {self.format_name()}{Greeting.format_punctuation()}"

    def format_name(self) -> str:
        return "Ada"

    @staticmethod
    def format_punctuation() -> str:
        return "!"
