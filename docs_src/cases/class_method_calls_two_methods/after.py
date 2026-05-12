class Greeting:
    def greet(self) -> str:
        return f"Hello, {self.format_name()}{self.format_punctuation()}"

    def format_name(self) -> str:
        return "Ada"

    def format_punctuation(self) -> str:
        return "!"
