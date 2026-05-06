from pystepdowner.analyzer import reformat_content


def format_code(source: str) -> str:
    return reformat_content(source.strip("\n")).strip("\n")
