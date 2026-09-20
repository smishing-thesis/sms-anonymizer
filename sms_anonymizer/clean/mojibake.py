import ftfy


def fix_mojibake(text: str) -> str:
    return ftfy.fix_text(text)
